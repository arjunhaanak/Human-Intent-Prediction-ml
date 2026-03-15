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
    
    case_id = f"case_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    data["id"] = case_id
    data["replies"] = [] # Initial empty replies
    file_path = os.path.join(DB_PATH, folder, f"{case_id}.json")
    
    with open(file_path, "w") as f:
        json.dump(data, f)
    return case_id

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
        case_id = save_to_db(result)
        result["id"] = case_id
        
        return result

        
    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/senior/login")
async def senior_login(data: dict):
    """Simple mockup login for senior workers."""
    if data.get("email") == "senior@aether.ai" and data.get("password") == "aether2026":
        return {"status": "success", "token": "premium_senior_token_uuid"}
    raise HTTPException(status_code=401, detail="Invalid Credentials")

@app.post("/suggest-reply")
async def suggest_reply(data: dict):
    """Generate an AI-drafted reply for the senior worker based on case intent and conversation."""
    import random
    case_id = data.get("case_id")
    intent = data.get("intent", "Neutral")
    last_customer_msg = data.get("last_customer_msg", "")
    confidence = data.get("confidence", 0.5)

    templates = {
        "Complaint": [
            f"Hello, I'm {{}}, a Senior Specialist at Aether. I've reviewed your case in full and I sincerely apologize for the experience you've had. "
            f"Your concern about \"{last_customer_msg[:60]}\" is completely valid. I'm personally escalating this to our resolutions team right now. "
            f"We'll have a concrete solution — whether a replacement, refund, or fix — within 24 hours. I'll be following up directly. You have my word.",

            f"Hi there, I've taken over your case as a Senior Specialist. I can see exactly what went wrong, and I want to make this right for you. "
            f"Regarding your issue: \"{last_customer_msg[:60]}\", I'm initiating a priority resolution right now. "
            f"Please expect a follow-up from our team within 24 hours. Thank you for your patience — it means a lot.",
        ],
        "Escalation": [
            f"Hi, I'm a Senior Specialist and I've taken personal ownership of your case. "
            f"I understand this is urgent — regarding \"{last_customer_msg[:60]}\", I'm treating this as top priority. "
            f"I've already flagged this internally. Please give me 30 minutes to coordinate with the relevant team and get back to you with a concrete action plan.",

            f"Thank you for your patience. As a Senior Specialist, I've reviewed your full conversation. "
            f"I can assure you this won't be dismissed. For your concern: \"{last_customer_msg[:60]}\", "
            f"I'm escalating this to our customer resolutions director. You'll receive a direct call or email within 2 hours.",
        ],
        "Distress": [
            f"I'm a Senior Specialist and I want you to know — we hear you and we're here for you. "
            f"I can see this situation is extremely stressful. I've immediately escalated your case to our emergency support team. "
            f"Someone will reach out to you directly within the next 15 minutes. Please stay calm — we will sort this out together.",

            f"Hi, your case has been marked as urgent and I've personally stepped in. "
            f"You don't have to handle this alone. I've notified our senior resolution team and they are aware of your situation. "
            f"You will hear back from us within 15 minutes. We take your concern very seriously.",
        ],
        "Inquiry": [
            f"Hello! I've reviewed your question: \"{last_customer_msg[:60]}\" "
            f"and I'm happy to give you a full and detailed answer. "
            f"Our AetherBook Ultra 14 features the Neural Chip M1 with 32GB RAM and 1TB SSD, priced at ₹1,56,900. "
            f"For audio, the Studio Pro ANC offers 40-hour battery with spatial audio. Would you like a comparison or recommendation based on your use case?",

            f"Great question! Regarding \"{last_customer_msg[:60]}\" — "
            f"I've pulled up the full details for you. Our Aether ecosystem is designed for seamless integration across devices. "
            f"The Vision Series starts at ₹20,500 and goes up to ₹1,56,900 depending on the product. "
            f"Let me know if you'd like pricing on a specific model or help with an order.",
        ],
        "Neutral": [
            f"Hi! I've reviewed your message: \"{last_customer_msg[:60]}\". "
            f"Everything looks good on our end. If you have any further questions about your order, products, or returns, I'm happy to help! "
            f"Is there anything specific you'd like me to look into for you?",

            f"Hello! Thanks for reaching out to Aether Support. I've reviewed your conversation and wanted to check in personally. "
            f"If you have any more questions or need assistance with anything — orders, returns, products, or technical support — just let me know!",
        ],
    }

    pool = templates.get(intent, templates["Neutral"])
    draft = random.choice(pool)
    # Format placeholder name
    draft = draft.format("Alex (Senior Specialist)")

    return {"draft": draft, "intent": intent}


@app.post("/escalate")
async def escalate_case(data: dict):
    """Customer marks themselves as not satisfied — attaches full conversation log."""
    case_id = data.get("case_id")
    conversation = data.get("conversation", [])

    for cat in ["priority", "neutral", "general"]:
        path = os.path.join(DB_PATH, cat, f"{case_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                case_data = json.load(f)
            case_data["escalated_by_user"] = True
            case_data["conversation_log"] = conversation
            case_data["escalation_time"] = datetime.now().isoformat()
            # Move to priority if not already there
            if cat != "priority":
                new_path = os.path.join(DB_PATH, "priority", f"{case_id}.json")
                os.replace(path, new_path)
                path = new_path
            with open(path, "w") as f:
                json.dump(case_data, f)
            return {"status": "escalated"}
    raise HTTPException(status_code=404, detail="Case not found")

@app.post("/dashboard/reply")
async def post_reply(data: dict):
    """Senior worker posts a reply to a case."""
    case_id = data.get("case_id")
    reply_text = data.get("reply")

    if not case_id or not reply_text:
        raise HTTPException(status_code=400, detail="case_id and reply are required")

    # Search all folders — always scan to be safe
    path = None
    for cat in ["priority", "neutral", "general"]:
        # Match by id field OR by filename
        folder = os.path.join(DB_PATH, cat)
        for filename in os.listdir(folder):
            fpath = os.path.join(folder, filename)
            try:
                with open(fpath, "r") as f:
                    cd = json.load(f)
                # Match by stored id OR by filename stem
                if cd.get("id") == case_id or filename.replace(".json", "") == case_id:
                    path = fpath
                    case_data = cd
                    break
            except Exception:
                continue
        if path:
            break

    if not path:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found in any queue")

    # Ensure replies list exists
    if "replies" not in case_data:
        case_data["replies"] = []

    case_data["replies"].append({
        "from": "Senior Specialist",
        "text": reply_text,
        "timestamp": datetime.now().isoformat()
    })

    with open(path, "w") as f:
        json.dump(case_data, f)

    print(f"✅ Senior replied to case {case_id}: {reply_text[:60]}")
    return {"status": "sent"}

@app.get("/case/{case_id}/replies")
async def get_case_replies(case_id: str):
    """Consumer polls for senior replies."""
    for cat in ["priority", "neutral", "general"]:
        folder = os.path.join(DB_PATH, cat)
        for filename in os.listdir(folder):
            fpath = os.path.join(folder, filename)
            try:
                with open(fpath, "r") as f:
                    cd = json.load(f)
                if cd.get("id") == case_id or filename.replace(".json", "") == case_id:
                    return {"replies": cd.get("replies", [])}
            except Exception:
                continue
    return {"replies": []}

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    stats = {}
    for folder in ["neutral", "priority", "general"]:
        path = os.path.join(DB_PATH, folder)
        stats[folder] = len(os.listdir(path))
    return stats

@app.get("/dashboard/cases/{category}")
async def get_cases(category: str):
    """Retrieves all cases, always injecting id from filename if missing."""
    path = os.path.join(DB_PATH, category)
    if not os.path.exists(path):
        return []
    cases = []
    for filename in os.listdir(path):
        fpath = os.path.join(path, filename)
        try:
            with open(fpath, "r") as f:
                data = json.load(f)
            # Always inject id from filename if not stored
            if "id" not in data or not data["id"]:
                data["id"] = filename.replace(".json", "")
            # Ensure replies list exists
            if "replies" not in data:
                data["replies"] = []
            cases.append(data)
        except Exception as e:
            print(f"Skipping corrupt file {filename}: {e}")
    return cases

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
