from transformers import pipeline
import torch
import os

class TextIntentModel:
    def __init__(self):
        # Initialize zero-shot classification pipeline using config
        from config import TEXT_MODEL
        model_name = TEXT_MODEL.get("model_name", "valhalla/distilbart-mnli-12-3")
        device = TEXT_MODEL.get("device", "cpu")
        
        try:
            from config import PERFORMANCE
            if PERFORMANCE.get("torch_threads"):
                torch.set_num_threads(PERFORMANCE["torch_threads"])

            # 1. Main intent classifier
            self.classifier = pipeline(
                "zero-shot-classification", 
                model=model_name,
                device=device,
                model_kwargs={"tie_word_embeddings": False}
            )

            # 2. Sentiment model for cross-validation (small & fast)
            self.sentiment_pipe = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=device
            )
            
            # Apply dynamic quantization for CPU speedup
            if device == "cpu" and PERFORMANCE.get("use_quantization"):
                try:
                    self.classifier.model = torch.quantization.quantize_dynamic(
                        self.classifier.model, {torch.nn.Linear}, dtype=torch.qint8
                    )
                    self.sentiment_pipe.model = torch.quantization.quantize_dynamic(
                        self.sentiment_pipe.model, {torch.nn.Linear}, dtype=torch.qint8
                    )
                    print("✅ Text & Sentiment models quantized for speed")
                except Exception as qe:
                    print(f"Quantization skipped: {qe}")

        except Exception as e:
            print(f"Warning: Could not load specific model, falling back to default: {e}")
            self.classifier = pipeline("zero-shot-classification")
            self.sentiment_pipe = None

        self.candidate_labels = ["Inquiry", "Complaint", "Escalation", "Distress", "Neutral"]

    def predict(self, text):
        """
        Predict intent from text with sentiment refinement.
        """
        if not text or not isinstance(text, str):
            return None, "Neutral", 0.0

        try:
            with torch.inference_mode():
                # 1. Zero-shot intent
                result = self.classifier(text, self.candidate_labels)
                scores = dict(zip(result['labels'], result['scores']))
                primary_intent = result['labels'][0]
                confidence = result['scores'][0]
                
                # 2. Sentiment cross-check (if enabled)
                if self.sentiment_pipe:
                    sent = self.sentiment_pipe(text)[0]
                    label = sent['label'] # POSITIVE or NEGATIVE
                    
                    # LOGIC: If sentiment is NEGATIVE and intent is inquiry/neutral, 
                    # check if we should boost Complaint or Escalation
                    if label == "NEGATIVE":
                        # If Inquiry is top but Complaint is strong competitor, swap
                        if primary_intent in ["Inquiry", "Neutral"]:
                            if scores.get("Complaint", 0) > 0.15:
                                primary_intent = "Complaint"
                                confidence = max(confidence, scores["Complaint"] * 1.2)
                            elif scores.get("Escalation", 0) > 0.15:
                                primary_intent = "Escalation"
                                confidence = max(confidence, scores["Escalation"] * 1.2)
                        
                        # Boost existing complaints/escalations
                        if primary_intent in ["Complaint", "Escalation"]:
                            confidence = min(0.99, confidence * 1.15)
                    
            return scores, primary_intent, confidence
            
        except Exception as e:
            print(f"Text prediction error: {e}")
            return None, "Error", 0.0
