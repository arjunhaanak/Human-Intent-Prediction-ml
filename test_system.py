"""
Quick Test Script for Intent Prediction System
This script tests each module independently before running the full app.
"""

import sys

def test_imports():
    """Test if all required packages are installed."""
    print("=" * 60)
    print("Testing Package Imports...")
    print("=" * 60)
    
    packages = {
        'streamlit': 'Streamlit',
        'torch': 'PyTorch',
        'transformers': 'Transformers',
        'cv2': 'OpenCV',
        'librosa': 'Librosa',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'PIL': 'Pillow'
    }
    
    failed = []
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"[OK] {name}: OK")
        except ImportError as e:
            print(f"[FAIL] {name}: FAILED - {e}")
            failed.append(name)
    
    if failed:
        print(f"\n[WARNING] Failed to import: {', '.join(failed)}")
        print("Please run: pip install -r requirements.txt")
        return False
    else:
        print("\n[SUCCESS] All packages imported successfully!")
        return True

def test_text_model():
    """Test text intent classification."""
    print("\n" + "=" * 60)
    print("Testing Text Intent Model...")
    print("=" * 60)
    
    try:
        from text_model import TextIntentModel
        
        model = TextIntentModel()
        print("[OK] Model loaded successfully")
        
        # Test prediction
        test_text = "I am very frustrated with your service!"
        scores, intent, conf = model.predict(test_text)
        
        print(f"\nTest Input: '{test_text}'")
        print(f"Predicted Intent: {intent}")
        print(f"Confidence: {conf:.2%}")
        print(f"All Scores: {scores}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Text model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fusion():
    """Test fusion logic."""
    print("\n" + "=" * 60)
    print("Testing Fusion Logic...")
    print("=" * 60)
    
    try:
        from fusion import fuse_multimodal
        
        # Test with mock data
        text_probs = {
            "Inquiry": 0.1,
            "Complaint": 0.7,
            "Escalation": 0.1,
            "Distress": 0.05,
            "Neutral": 0.05
        }
        
        audio_emotion = ("angry", 0.85)
        
        intent, conf, scores, action = fuse_multimodal(
            text_probs=text_probs,
            audio_emotion=audio_emotion
        )
        
        print(f"[OK] Fusion successful")
        print(f"Final Intent: {intent}")
        print(f"Confidence: {conf:.2%}")
        print(f"Action: {action}")
        print(f"All Scores: {scores}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Fusion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("INTENT PREDICTION SYSTEM - TEST SUITE")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n[FAIL] Import test failed. Please install dependencies first.")
        sys.exit(1)
    
    # Test text model (most critical)
    if not test_text_model():
        print("\n[WARNING] Text model test failed. The app may not work properly.")
        print("This is usually due to missing models. They will download on first run.")
    
    # Test fusion
    if not test_fusion():
        print("\n[FAIL] Fusion test failed. Please check the code.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] BASIC TESTS PASSED!")
    print("=" * 60)
    print("\nYou can now run the full application with:")
    print("  streamlit run app.py")
    print("\nNote: Audio and Vision models will download on first use (~1-2 GB)")

if __name__ == "__main__":
    main()
