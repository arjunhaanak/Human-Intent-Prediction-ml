"""
Configuration file for model settings and hyperparameters.
Modify these settings to customize the application behavior.
"""

# ============================================================================
# MODEL CONFIGURATIONS
# ============================================================================

# Text Model Configuration
TEXT_MODEL = {
    "model_name": "valhalla/distilbart-mnli-12-3",
    "fallback_model": "facebook/bart-large-mnli",  # If primary fails
    "task": "zero-shot-classification",
    "device": "cpu",  # Change to "cuda" if you have GPU
}

# Audio Model Configuration
AUDIO_MODEL = {
    "model_name": "Dpngtm/wav2vec2-emotion-recognition",  # Robust base-sized model
    "task": "audio-classification",
    "device": "cpu",
    "sample_rate": 16000,
}

# Vision Model Configuration
VISION_MODEL = {
    "model_name": "dima806/facial_emotions_image_detection",
    "task": "image-classification",
    "device": "cpu",  # Change to "cuda" if you have GPU
    "face_detection": "haarcascade_frontalface_default.xml",
    "min_face_size": (30, 30),
    "scale_factor": 1.1,
    "min_neighbors": 5,
}

# ============================================================================
# FUSION CONFIGURATIONS
# ============================================================================

# Default weights for each modality (when all are present)
# These will be normalized automatically
FUSION_WEIGHTS = {
    "text": 0.5,    # Text is usually most accurate for intent
    "audio": 0.3,   # Audio provides emotional context
    "vision": 0.2,  # Vision adds facial emotion cues
}

# Intent classes (do not modify unless you retrain models)
INTENT_CLASSES = [
    "Inquiry",
    "Complaint", 
    "Escalation",
    "Distress",
    "Neutral"
]

# Emotion to Intent mapping (heuristic rules)
# Format: emotion -> [Inquiry, Complaint, Escalation, Distress, Neutral]
EMOTION_TO_INTENT_MAP = {
    "angry":      [0.0, 0.4, 0.5, 0.1, 0.0],
    "happy":      [0.6, 0.0, 0.0, 0.0, 0.4],
    "sad":        [0.1, 0.2, 0.0, 0.7, 0.0],
    "fear":       [0.0, 0.0, 0.1, 0.9, 0.0],
    "fearful":    [0.0, 0.0, 0.1, 0.9, 0.0],
    "neutral":    [0.5, 0.0, 0.0, 0.0, 0.5],
    "calm":       [0.5, 0.0, 0.0, 0.0, 0.5],
    "surprise":   [0.5, 0.1, 0.1, 0.2, 0.1],
    "disgust":    [0.0, 0.6, 0.2, 0.1, 0.1],
}

# ============================================================================
# ACTION RECOMMENDATION RULES
# ============================================================================

# Confidence thresholds for action recommendations
ACTION_THRESHOLDS = {
    "high_confidence": 0.6,  # Above this = automatic escalation
    "medium_confidence": 0.4, # Above this = priority handling
}

# Action mapping based on intent and confidence
# Format: {intent: {confidence_level: action}}
ACTION_RULES = {
    "Inquiry": "Normal routing",
    "Neutral": "Normal routing",
    "Complaint": {
        "high": "Automatic escalation",
        "medium": "Priority handling",
        "low": "Normal routing"
    },
    "Escalation": {
        "high": "Automatic escalation",
        "medium": "Priority handling",
        "low": "Priority handling"
    },
    "Distress": "Immediate Human Agent",  # Always urgent
}

# ============================================================================
# UI CONFIGURATIONS
# ============================================================================

UI_CONFIG = {
    "page_title": "Real-Time Adaptive Multimodal Human Intent Prediction",
    "page_icon": "🧠",
    "layout": "wide",
    "sidebar_state": "expanded",
    "theme": {
        "primaryColor": "#1E88E5",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6",
        "textColor": "#262730",
    }
}

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

PERFORMANCE = {
    "cache_models": True,  # Cache loaded models in memory
    "max_audio_duration": 30,  # Maximum audio duration in seconds
    "max_image_size": (1920, 1080),  # Maximum image resolution
    "enable_gpu": False,  # Set to True if you have CUDA-capable GPU
    "use_quantization": True,  # Quantize models for 2-3x speedup on CPU
    "torch_threads": 4,  # Number of threads for torch to use
}

# ============================================================================
# LOGGING AND DEBUGGING
# ============================================================================

DEBUG = {
    "verbose": True,  # Print detailed logs
    "show_timing": False,  # Show inference timing
    "save_predictions": False,  # Save predictions to file
    "log_file": "predictions.log",
}

# ============================================================================
# ADVANCED SETTINGS (For experimentation)
# ============================================================================

ADVANCED = {
    # Minimum confidence threshold to consider a prediction valid
    "min_confidence_threshold": 0.1,
    
    # Whether to apply softmax normalization to fusion outputs
    "apply_softmax": False,
    
    # Temperature for softmax (if enabled)
    "temperature": 1.0,
    
    # Whether to use weighted average or max pooling for fusion
    "fusion_method": "weighted_average",  # Options: weighted_average, max_pooling
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_action_for_intent(intent, confidence):
    """
    Determine the recommended action based on intent and confidence.
    
    Args:
        intent (str): Predicted intent
        confidence (float): Confidence score (0-1)
        
    Returns:
        str: Recommended action
    """
    if intent not in ACTION_RULES:
        return "Normal routing"
    
    rule = ACTION_RULES[intent]
    
    # If rule is a string, return it directly
    if isinstance(rule, str):
        return rule
    
    # If rule is a dict, determine based on confidence
    if confidence >= ACTION_THRESHOLDS["high_confidence"]:
        return rule.get("high", "Priority handling")
    elif confidence >= ACTION_THRESHOLDS["medium_confidence"]:
        return rule.get("medium", "Normal routing")
    else:
        return rule.get("low", "Normal routing")

def validate_config():
    """Validate configuration settings."""
    assert len(INTENT_CLASSES) > 0, "INTENT_CLASSES cannot be empty"
    assert sum(FUSION_WEIGHTS.values()) > 0, "FUSION_WEIGHTS must sum to positive value"
    
    for emotion, probs in EMOTION_TO_INTENT_MAP.items():
        assert len(probs) == len(INTENT_CLASSES), \
            f"Emotion '{emotion}' mapping length mismatch"
    
    print("✅ Configuration validated successfully")

if __name__ == "__main__":
    validate_config()
    print("\n📋 Current Configuration:")
    print(f"  Intent Classes: {INTENT_CLASSES}")
    print(f"  Fusion Weights: {FUSION_WEIGHTS}")
    print(f"  Text Model: {TEXT_MODEL['model_name']}")
    print(f"  Audio Model: {AUDIO_MODEL['model_name']}")
    print(f"  Vision Model: {VISION_MODEL['model_name']}")
