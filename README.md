# Real-Time Adaptive Multimodal Human Intent Prediction

A Python-based AI application that predicts human/customer intent in real-time using text, voice, and facial emotion inputs with adaptive multimodal fusion.

## 🎯 Features

- **Text Intent Classification**: Zero-shot learning using BERT/DistilBART
- **Voice Emotion Recognition**: Wav2Vec2-based audio emotion detection
- **Facial Emotion Detection**: Vision Transformer with OpenCV face detection
- **Adaptive Multimodal Fusion**: Smart fusion with **agreement boosting** & confidence weighting
- **Modern Interactive UI**: Stunning gradient design with **Plotly** visualizations
- **Video Support**: Extract audio from **MP4/AVI/MOV** files automatically
- **Live Input**: Real-time audio recording & webcam capture
- **Real-time Predictions**: Fast inference with pre-trained models

## 📋 Intent Classes

The system predicts one of the following intents:
- **Inquiry**: Customer asking questions or seeking information
- **Complaint**: Customer expressing dissatisfaction
- **Escalation**: Customer demanding higher-level support
- **Distress**: Customer in urgent need or emotional distress
- **Neutral**: General conversation

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- Webcam (optional, for facial emotion detection)
- Microphone or audio files (optional, for voice emotion)

### Setup Steps

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

**Note**: First-time installation will download several pre-trained models (~1-2 GB total). Ensure you have a stable internet connection.

## 🚀 Running the Application

1. **Start the Streamlit app**:
```bash
streamlit run app.py
```

2. **Open your browser** to the URL shown (typically `http://localhost:8501`)

3. **Use the application**:
   - Enable desired modalities (Text, Audio, Vision)
   - Input your data:
     - **Text**: Type a customer message
     - **Audio/Video**: Upload **.wav, .mp3, .mp4, .avi** (video audio extracted automatically!)
     - **Live Voice**: Click microphone to record
     - **Vision**: Capture from webcam or upload image
   - Click "Predict Intent"
   - View results with confidence scores and recommended actions

## 📁 Project Structure

```
Human intent Prediction/
├── app.py                 # Main Streamlit application
├── text_model.py          # Text intent classification module
├── audio_model.py         # Audio emotion recognition module
├── vision_model.py        # Facial emotion detection module
├── fusion.py              # Adaptive multimodal fusion logic
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🧠 How It Works

### 1. Text Analysis
- Uses zero-shot classification with DistilBART/BERT
- Directly predicts intent from customer message
- Returns probability distribution over all intent classes

### 2. Audio Analysis
- Processes audio files using Wav2Vec2
- Detects emotions: angry, happy, sad, fear, neutral, surprise, disgust
- Maps emotions to intent probabilities using heuristic rules

### 3. Vision Analysis
- Detects faces using OpenCV Haar Cascades
- Classifies facial expressions using Vision Transformer
- Extracts emotion from largest detected face

### 4. Adaptive Fusion
- Combines available modalities dynamically
- Applies confidence-weighted averaging
- Redistributes weights if modalities are missing
- Default weights: Text (50%), Audio (30%), Vision (20%)

### 5. Action Recommendation
Based on predicted intent and confidence:
- **Normal routing**: Inquiry or Neutral
- **Priority handling**: Complaint or Escalation (moderate confidence)
- **Automatic escalation**: Complaint or Escalation (high confidence)
- **Immediate Human Agent**: Distress

## 🎨 Example Usage

### Example 1: Text Only
**Input**: "I am very frustrated with your service and need to speak to a manager immediately!"

**Output**:
- Intent: Escalation
- Confidence: 87%
- Action: Automatic escalation

### Example 2: Multimodal (Text + Audio)
**Text**: "I have a question about my order"
**Audio**: Calm, neutral tone

**Output**:
- Intent: Inquiry
- Confidence: 92%
- Action: Normal routing

### Example 3: All Modalities
**Text**: "This is unacceptable!"
**Audio**: Angry tone
**Vision**: Angry facial expression

**Output**:
- Intent: Complaint
- Confidence: 95%
- Action: Automatic escalation

## 🔧 Troubleshooting

### Models not loading
- Ensure stable internet connection for first-time download
- Check available disk space (~2 GB needed)
- Try clearing Hugging Face cache: `rm -rf ~/.cache/huggingface/`

### Webcam not working
- Grant browser permission to access camera
- Check if camera is being used by another application
- Use image upload as alternative

### Audio file errors
- Ensure audio is in supported format (.wav, .mp3, .ogg)
- Check file is not corrupted
- Try converting to .wav using audio editing software

### Slow predictions
- First prediction is slower due to model loading (cached afterwards)
- Vision model is most computationally intensive
- Consider using CPU-optimized models for faster inference

## 📊 Technical Details

### Models Used
- **Text**: `valhalla/distilbart-mnli-12-3` (Zero-shot classification)
- **Audio**: `ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition`
- **Vision**: `dima806/facial_emotions_image_detection` (ViT-based)

### Dependencies
- Streamlit: Web UI framework
- Transformers: Hugging Face model library
- PyTorch: Deep learning backend
- OpenCV: Computer vision operations
- Librosa: Audio processing
- NumPy, Pandas: Data manipulation

## 🎓 For Academic/Viva Purposes

This project demonstrates:
1. **Multimodal AI**: Integration of text, audio, and vision
2. **Transfer Learning**: Using pre-trained models
3. **Adaptive Systems**: Dynamic weight adjustment based on available inputs
4. **Real-world Application**: Customer service automation
5. **Software Engineering**: Modular, maintainable code structure

### Key Concepts Explained
- **Zero-shot Learning**: Classify without task-specific training
- **Emotion-Intent Mapping**: Heuristic rules linking emotions to intents
- **Confidence Weighting**: More confident predictions have higher influence
- **Graceful Degradation**: System works even if modalities are missing

## 📝 License

This project is for educational purposes. Pre-trained models are subject to their respective licenses.

## 🤝 Contributing

This is an educational project. Feel free to extend it with:
- Additional intent classes
- More sophisticated fusion algorithms
- Real-time audio streaming
- Multi-language support
- Custom model fine-tuning

## 📧 Support

For issues or questions, please check:
1. This README
2. Error messages in the Streamlit interface
3. Console output for detailed logs

---

**Built with ❤️ for Real-Time Human Intent Prediction**
