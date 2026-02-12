
import cv2
import numpy as np
import torch
import os
import time
from PIL import Image
from transformers import pipeline

class VisionEmotionModel:
    def __init__(self):
        # Using a standard Vision Transformer for facial expression recognition
        # dima806/facial_emotions_image_detection is a ViT tuned on FER2013 or simliar
        # Output labels: "angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"
        try:
            self.classifier = pipeline(
                "image-classification", 
                model="dima806/facial_emotions_image_detection",
                use_fast=False
            )
        except Exception:
            # Fallback to smaller model if needed, but ViT is standard size ~300MB
            self.classifier = None
            print("Vision model loading failed. Check internet connection or disk space.")

        # Load OpenCV Face Detector (Haar Cascade)
        # Using built-in path
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_face(self, image_array):
        """
        Detect faces in an image (numpy array or PIL Image).
        Returns list of (x, y, w, h).
        """
        if isinstance(image_array, Image.Image):
            image_array = np.array(image_array)

        # Convert to BGR for OpenCV if it's RGB (Streamlit/PIL)
        if image_array.ndim == 3 and image_array.shape[2] == 3:
           gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        elif image_array.ndim == 2:
           gray = image_array
        else:
           return []

        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces

    def predict(self, input_image):
        """
        Predict emotion from the largest face in the image.
        Args:
            input_image: PIL Image or numpy array (RGB)
        Returns:
            label (str), confidence (float), boxed_image (numpy array for display)
        """
        if self.classifier is None:
            return "Model Error", 0.0, input_image

        # Ensure correct format for OpenCV
        if isinstance(input_image, Image.Image):
            frame = np.array(input_image)
        else:
            frame = input_image

        faces = self.detect_face(frame)
        
        if len(faces) == 0:
            return None, 0.0, frame

        # Get largest face
        largest_face = max(faces, key=lambda r: r[2] * r[3])
        x, y, w, h = largest_face
        
        # Crop face
        # Add some margin
        margin = int(0.1 * h)
        y1 = max(0, y - margin)
        y2 = min(frame.shape[0], y + h + margin)
        x1 = max(0, x - margin)
        x2 = min(frame.shape[1], x + w + margin)
        
        face_crop = frame[y1:y2, x1:x2]
        
        # Convert crop back to PIL for Transformers
        pil_face = Image.fromarray(face_crop)

        # Predict
        try:
            start_time = time.time()
            results = self.classifier(pil_face)
            # format: [{'label': 'happy', 'score': 0.99}, ...]
            top_result = results[0]
            label = top_result['label']
            score = top_result['score']
            
            # Draw on frame
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"{label}: {score:.2f}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        
            return label, score, frame
            
        except Exception as e:
            print(f"Vision prediction error: {e}")
            return None, 0.0, frame
