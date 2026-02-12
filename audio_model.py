import torch
import librosa
import numpy as np
import io
import tempfile
import os
from transformers import pipeline

class AudioEmotionModel:
    def __init__(self):
        # We use a more robust model for emotion recognition
        # 'haru-recording/wav2vec2-lg-xlsr-en-speech-emotion-recognition' is generally seen as very accurate
        # Emotions: 'angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise'
        try:
            print("Loading Audio Model: ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition...")
            self.pipeline = pipeline(
                "audio-classification", 
                model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
                device="cpu" # Force CPU for stability on most devices
            )
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
                    y, sr = librosa.load(tmp_path, sr=16000)
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

            if y is None or len(y) == 0:
                return None, 0.0

            # 2. FEATURE EXTRACTION (Satisfying system requirements)
            features = self.extract_features(y, sr)
            
            # 3. PREDICT
            # Pass the raw numpy array to the pipeline
            # The pipeline handles the tensor conversion internally
            results = self.pipeline(y)
            
            # Result format: [{'score': 0.9, 'label': 'angry'}, ...]
            if not results:
                return "neutral", 0.5

            # The model labels might be differentAUTHOR's specific capitalization
            top_result = results[0]
            label = top_result['label'].lower()
            score = top_result['score']
            
            # Print detailed results for debugging
            print(f"Audio Prediction Results: {results[:3]}")
            
            return label, score
            
        except Exception as e:
            print(f"Audio prediction error: {e}")
            import traceback
            traceback.print_exc()
            return "neutral", 0.0
