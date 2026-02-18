import torch
import librosa
import numpy as np
import io
import tempfile
import os
from transformers import pipeline

class AudioEmotionModel:
    def __init__(self):
        # Configuration-driven loading
        from config import AUDIO_MODEL
        model_name = AUDIO_MODEL.get("model_name", "AventIQ-AI/wav2vec2-base_speech_emotion_recognition")
        device = AUDIO_MODEL.get("device", "cpu")
        
        try:
            from config import PERFORMANCE
            if PERFORMANCE.get("torch_threads"):
                torch.set_num_threads(PERFORMANCE["torch_threads"])

            print(f"Loading Audio Model: {model_name}...")
            self.pipeline = pipeline(
                "audio-classification", 
                model=model_name,
                device=device
            )
            
            # Disable quantization for now to rule it out as a cause of failure
            if device == "cpu" and PERFORMANCE.get("use_quantization"):
                try:
                    self.pipeline.model = torch.quantization.quantize_dynamic(
                        self.pipeline.model, {torch.nn.Linear}, dtype=torch.qint8
                    )
                    print("✅ Audio model quantized for speed")
                except Exception as qe:
                    print(f"Quantization skipped: {qe}")
            
            print(f"✅ Audio model loaded: {self.pipeline is not None}")

        except Exception as e:
            print(f"⚠️ Failed to load audio model: {e}")
            self.pipeline = None

    def extract_features(self, audio_array, sr=16000):
        """
        Extract MFCC and other features using Librosa.
        This provides technical details for the UI.
        """
        try:
            # Extract 13 MFCCs
            mfccs = librosa.feature.mfcc(y=audio_array, sr=sr, n_mfcc=13)
            # Calculate mean across time for a summary vector
            mfccs_mean = np.mean(mfccs.T, axis=0)
            
            # Extract Chroma features (tonal representation)
            chroma = librosa.feature.chroma_stft(y=audio_array, sr=sr)
            chroma_mean = np.mean(chroma.T, axis=0)
            
            return {
                "mfcc": mfccs_mean.tolist(),
                "chroma": chroma_mean.tolist(),
                "tempo": float(librosa.beat.beat_track(y=audio_array, sr=sr)[0])
            }
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None

    def predict(self, audio_input):
        """
        Predict emotion from audio.
        Handles file paths, file-like objects, or raw bytes.
        """
        if self.pipeline is None:
            return "neutral", 0.0

        try:
            # 1. LOAD AND PREPROCESS AUDIO
            # Ensuring 16kHz mono is CRITICAL for Wav2Vec2 accuracy
            y, sr = None, 16000
            
            if isinstance(audio_input, str):
                # Load from path
                y, sr = librosa.load(audio_input, sr=16000)
            else:
                # Handle file-like objects (from Streamlit)
                # Create a temp file to ensure librosa can read it regardless of format
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    audio_input.seek(0)
                    tmp.write(audio_input.read())
                    tmp_path = tmp.name
                
                try:
                    print(f"Loading via Librosa from temp path: {tmp_path}")
                    y, sr = librosa.load(tmp_path, sr=16000)
                    print(f"Librosa loaded successfully. Array size: {len(y) if y is not None else 0}")
                except Exception as le:
                    print(f"Librosa load error: {le}")
                    y, sr = None, 16000
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

            if y is None or len(y) == 0:
                print("⚠️ CRITICAL: Audio array is empty or None after processing")
                return "neutral", 0.0 # Return fallback instead of None to prevent app failure

            # 2. FEATURE EXTRACTION (Satisfying system requirements)
            features = self.extract_features(y, sr)
            
            # 3. PREDICT
            print(f"Sending audio to pipeline (array shape: {y.shape})")
            with torch.inference_mode():
                results = self.pipeline(y)
            
            print(f"Audio raw results: {results}")
            
            # Result format: [{'score': 0.9, 'label': 'angry'}, ...]
            if not results or not isinstance(results, list):
                print(f"⚠️ Unexpected results format: {results}")
                return "neutral", 0.0

            top_result = results[0]
            label = str(top_result.get('label', 'neutral')).lower()
            score = float(top_result.get('score', 0.0))
            
            # Print detailed results for debugging
            print(f"Audio Prediction Results: {results[:3]}")
            
            return label, score
            
        except Exception as e:
            print(f"Audio prediction error: {e}")
            import traceback
            traceback.print_exc()
            return "neutral", 0.0
