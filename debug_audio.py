import torch
import librosa
import numpy as np
from transformers import pipeline
import os
import sys

# Set encoding for windows terminal to avoid UnicodeEncodeError
sys.stdout.reconfigure(encoding='utf-8')

def test_audio_model():
    model_name = "AventIQ-AI/wav2vec2-base_speech_emotion_recognition"
    print(f"Testing model: {model_name}")
    
    try:
        # Load pipeline
        print("Loading pipeline...")
        pipe = pipeline("audio-classification", model=model_name)
        print("Pipeline loaded")
        
        # Create dummy audio (1 second of silence/noise)
        sr = 16000
        dummy_audio = np.random.uniform(-1, 1, sr).astype(np.float32)
        
        # Test basic prediction
        print("Testing basic prediction...")
        results = pipe(dummy_audio)
        print(f"Basic results: {results}")
        
    except Exception as e:
        print(f"Model testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_model()
