import json

import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import io
from PIL import Image
import numpy as np
from text_model import TextIntentModel
from audio_model import AudioEmotionModel
from vision_model import VisionEmotionModel
from fusion import fuse_multimodal, INTENT_CLASSES

app = FastAPI(title="Neural Intent API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models (singletons, loaded once)
print("🚀 Initializing Neural Core for API Server...")
text_engine = TextIntentModel()
audio_engine = AudioEmotionModel()
vision_engine = VisionEmotionModel()
print("✅ Models synchronized and ready.")

# Database Simulation Paths
DB_PATH = "d:/Human intent Prediction/db"
for folder in ["neutral", "priority", "general"]:
    os.makedirs(os.path.join(DB_PATH, folder), exist_ok=True)

def save_to_db(data):
    """Saves the prediction to a specific folder based on intent."""
    intent = data.get("intent", "Neutral")
    
    # Category mapping for Senior Workers
    if intent in ["Escalation", "Distress", "Complaint"]:
        folder = "priority"
    elif intent == "Neutral":
        folder = "neutral"
    else:
        folder = "general"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_path = os.path.join(DB_PATH, folder, f"case_{timestamp}.json")
    
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path

@app.post("/predict")
async def predict_intent(
    text: str = Form(None),
    audio: UploadFile = File(None),
    image: UploadFile = File(None)
):
    """
    Main multimodal prediction endpoint.
    Recieves text, audio file, or image file.
    """
    try:
        text_probs = None
        audio_emotion = None
        vision_emotion = None
        
        # 1. Process Text
        if text:
            scores, _, _ = text_engine.predict(text)
            text_probs = scores
            
        # 2. Process Audio
        if audio:
            audio_bytes = await audio.read()
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = audio.filename
            label, conf = audio_engine.predict(audio_file)
            if label:
                audio_emotion = (label, conf)
                
        # 3. Process Vision
        if image:
            image_bytes = await image.read()
            pil_image = Image.open(io.BytesIO(image_bytes))
            label, conf, _ = vision_engine.predict(pil_image)
            if label:
                vision_emotion = (label, conf)
                
        # 4. Fusion
        # Default weights
        weights = {'text': 0.45, 'audio': 0.35, 'vision': 0.20}
        
        final_intent, final_conf, all_scores, action, modality_probs = fuse_multimodal(
            text_probs=text_probs,
            audio_emotion=audio_emotion,
            vision_emotion=vision_emotion,
            weights=weights
        )
        
        result = {
            "intent": final_intent,
            "confidence": float(final_conf),
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "text_input": text if text else "N/A"
        }
        
        # Save for dashboard
        save_to_db(result)
        
        return result

        
    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Returns counts for the dashboard sections."""
    stats = {}
    for folder in ["neutral", "priority", "general"]:
        path = os.path.join(DB_PATH, folder)
        stats[folder] = len(os.listdir(path))
    return stats

@app.get("/dashboard/cases/{category}")
async def get_cases(category: str):
    """Retrieves all cases for a specific category."""
    path = os.path.join(DB_PATH, category)
    if not os.path.exists(path):
        return []
    
    cases = []
    for filename in os.listdir(path):
        with open(os.path.join(path, filename), "r") as f:
            cases.append(json.load(f))
    return cases


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
