from transformers import pipeline

class TextIntentModel:
    def __init__(self):
        # Initialize zero-shot classification pipeline
        # Using a smaller distilled model for speed if possible, else standard bart-large
        try:
            self.classifier = pipeline(
                "zero-shot-classification", 
                model="valhalla/distilbart-mnli-12-3",
                model_kwargs={"tie_word_embeddings": False}
            )
        except Exception as e:
            print(f"Warning: Could not load specific model, falling back to default: {e}")
            self.classifier = pipeline("zero-shot-classification")

        self.candidate_labels = ["Inquiry", "Complaint", "Escalation", "Distress", "Neutral"]

    def predict(self, text):
        """
        Predict intent from text.
        Args:
            text (str): Input text.
        Returns:
            dict: {intent: score} map for all candidate labels.
            primary_intent (str): The top predicted label.
            confidence (float): The score of the top label.
        """
        if not text or not isinstance(text, str):
            return None, "Neutral", 0.0

        try:
            result = self.classifier(text, self.candidate_labels)
            
            # Result format: {'labels': [...], 'scores': [...]}
            scores = dict(zip(result['labels'], result['scores']))
            primary_intent = result['labels'][0]
            confidence = result['scores'][0]
            
            return scores, primary_intent, confidence
            
        except Exception as e:
            print(f"Text prediction error: {e}")
            return None, "Error", 0.0
