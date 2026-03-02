import numpy as np

# Define global intent classes
INTENT_CLASSES = ["Inquiry", "Complaint", "Escalation", "Distress", "Neutral"]

# OPTIMIZED emotion to intent mapping weights for highest accuracy
# Rows: Emotions, Cols: Intents (Inquiry, Complaint, Escalation, Distress, Neutral)
EMOTION_TO_INTENT_MAP = {
    "angry":      [0.0, 0.15, 0.75, 0.10, 0.0],  # Heavy focus on Escalation
    "happy":      [0.80, 0.0, 0.0, 0.0, 0.20],   # Very strong Inquiry (customer is satisfied/asking)
    "sad":        [0.05, 0.10, 0.0, 0.80, 0.05], # Very strong Distress
    "fear":       [0.0, 0.0, 0.10, 0.90, 0.0],   # Almost 100% Distress
    "fearful":    [0.0, 0.0, 0.10, 0.90, 0.0],
    "neutral":    [0.40, 0.0, 0.0, 0.0, 0.60],   # Mostly Neutral/Inquiry
    "calm":       [0.40, 0.0, 0.0, 0.0, 0.60],
    "surprise":   [0.70, 0.10, 0.10, 0.05, 0.05],# Surprise often means Inquiry
    "surprised":  [0.70, 0.10, 0.10, 0.05, 0.05],
    "disgust":    [0.0, 0.85, 0.10, 0.05, 0.0],  # Heavy focus on Complaint
    "frustrated": [0.0, 0.50, 0.50, 0.0, 0.0],   # Split between Complaint and Escalation
    "worried":    [0.10, 0.10, 0.0, 0.80, 0.0],
    "confused":   [0.85, 0.05, 0.0, 0.05, 0.05], # Confusion is usually an Inquiry
    # Short codes
    "ang":        [0.0, 0.15, 0.75, 0.10, 0.0],
    "hap":        [0.80, 0.0, 0.0, 0.0, 0.20],
    "neu":        [0.40, 0.0, 0.0, 0.0, 0.60],
}

def normalize(probs):
    """Normalize a list of probabilities to sum to 1."""
    s = sum(probs)
    if s == 0:
        return [1.0 / len(probs)] * len(probs)
    return [p / s for p in probs]

def map_emotion_to_intent_probs(emotion_label, confidence):
    """
    Maps an emotion label (e.g., 'angry') to a probability distribution over intents.
    Returns a probability list matching INTENT_CLASSES.
    """
    emotion_key = emotion_label.lower()
    
    # improved matching for various model outputs
    base_probs = [0.2, 0.2, 0.2, 0.2, 0.2] # Default uniform
    
    # Check for exact match first, then substring
    if emotion_key in EMOTION_TO_INTENT_MAP:
        base_probs = EMOTION_TO_INTENT_MAP[emotion_key]
    else:
        for key, probs in EMOTION_TO_INTENT_MAP.items():
            if key in emotion_key:
                base_probs = probs
                break
            
    # Apply confidence scaling: IF confidence is high, trust the map fully
    # If confidence is low (<0.4), pull towards uniform
    
    if confidence < 0.3:
        # Too low confidence, just return uniform
        return [0.2] * 5
        
    # We use a simple blending but with a steeper curve
    # At conf=1.0 -> 100% map. At conf=0.0 -> 100% uniform.
    uniform = [0.2] * 5
    
    final_probs = []
    for i in range(len(base_probs)):
        p = confidence * base_probs[i] + (1 - confidence) * uniform[i]
        final_probs.append(p)
        
    return normalize(final_probs)

def fuse_multimodal(text_probs=None, audio_emotion=None, vision_emotion=None, weights=None):
    """
    ENHANCED Adaptive Multimodal fusion with agreement detection.
    
    Args:
        text_probs (dict): {intent: score} from text model.
        audio_emotion (tuple): (label, score) from audio model.
        vision_emotion (tuple): (label, score) from vision model.
        weights (dict): Optional dictionary of weights for 'text', 'audio', 'vision'.
        
    Returns:
        final_intent: string
        final_confidence: float
        all_scores: dict {intent: score}
        action: string
    """
    
    # 1. Initialize logic containers
    # Default weights if not provided
    if weights is None:
        weights = {'text': 0.45, 'audio': 0.35, 'vision': 0.20}
        
    W_TEXT = weights.get('text', 0.45)
    W_AUDIO = weights.get('audio', 0.35)
    W_VISION = weights.get('vision', 0.20)
    
    active_weights = {}
    modality_probs = {}
    modality_top_intents = {}  # Track top intent per modality
    
    # 2. Process Text
    if text_probs:
        vec = [text_probs.get(c, 0.0) for c in INTENT_CLASSES]
        modality_probs['text'] = vec
        active_weights['text'] = W_TEXT
        modality_top_intents['text'] = INTENT_CLASSES[np.argmax(vec)]
    
    # 3. Process Audio
    if audio_emotion:
        label, score = audio_emotion
        vec = map_emotion_to_intent_probs(label, score)
        modality_probs['audio'] = vec
        active_weights['audio'] = W_AUDIO
        modality_top_intents['audio'] = INTENT_CLASSES[np.argmax(vec)]

    # 4. Process Vision
    if vision_emotion:
        label, score = vision_emotion
        vec = map_emotion_to_intent_probs(label, score)
        modality_probs['vision'] = vec
        active_weights['vision'] = W_VISION
        modality_top_intents['vision'] = INTENT_CLASSES[np.argmax(vec)]
        
    # 5. Adaptive Normalization
    total_weight = sum(active_weights.values())
    
    if total_weight == 0:
        # Fallback if nothing is provided
        return "Neutral", 0.0, {k: 0.2 for k in INTENT_CLASSES}, "Normal routing", {}

        
    # 6. Weighted Fusion
    final_vector = np.zeros(len(INTENT_CLASSES))
    
    for mod, vec in modality_probs.items():
        weight = active_weights[mod] / total_weight # Normalize weight dynamically
        final_vector += np.array(vec) * weight
        
    # 7. CONFIDENCE BOOSTING: Check for modality agreement
    # If multiple modalities predict the same intent, boost confidence
    if len(modality_top_intents) >= 2:
        top_intents = list(modality_top_intents.values())
        # Count how many modalities agree on the most common intent
        from collections import Counter
        intent_counts = Counter(top_intents)
        most_common_intent, count = intent_counts.most_common(1)[0]
        
        if count >= 2:  # At least 2 modalities agree
            # Boost the confidence for the agreed-upon intent
            intent_idx = INTENT_CLASSES.index(most_common_intent)
            boost_factor = 1.0 + (0.15 * (count - 1))  # 15% boost per additional agreement
            final_vector[intent_idx] *= boost_factor
            
    # Renormalize after boosting
    final_vector = normalize(final_vector.tolist())
        
    # 8. Result Extraction
    best_idx = np.argmax(final_vector)
    best_intent = INTENT_CLASSES[best_idx]
    best_conf = final_vector[best_idx]
    
    # Map to output format
    all_scores = {INTENT_CLASSES[i]: final_vector[i] for i in range(len(INTENT_CLASSES))}
    
    # 9. PREMIUM ACTION PROTOCOLS (Tiered Intelligence)
    if best_intent == "Distress":
        action = "CRITICAL: EMERGENCY HUMAN HAND-OFF"
    elif best_intent == "Escalation":
        if best_conf > 0.65:
            action = "TIER-3 PRIORITY MANAGEMENT"
        else:
            action = "TIER-2 SUPERVISOR ALERT"
    elif best_intent == "Complaint":
        if best_conf > 0.70:
            action = "IMMEDIATE SERVICE RESOLUTION"
        elif best_conf > 0.45:
            action = "PRIORITY QUALITY REVIEW"
        else:
            action = "STANDARD FEEDBACK PROCESSING"
    elif best_intent == "Inquiry":
        if best_conf > 0.80:
            action = "AI AUTOMATED KB MATCHING"
        else:
            action = "STANDARD INQUIRY QUEUE"
    else:  # Neutral
        action = "ROUTINE SYSTEMATIC ROUTING"
        
    return best_intent, best_conf, all_scores, action, modality_probs
