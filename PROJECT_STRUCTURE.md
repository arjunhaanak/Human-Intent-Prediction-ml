# Project Structure and File Descriptions

## 📁 Complete File Overview

```
d:/Human intent Prediction/
│
├── 📄 app.py                    # Main Streamlit application (RUN THIS)
├── 📄 text_model.py             # Text intent classification module
├── 📄 audio_model.py            # Audio emotion recognition module
├── 📄 vision_model.py           # Facial emotion detection module
├── 📄 fusion.py                 # Adaptive multimodal fusion logic
├── 📄 config.py                 # Configuration and settings
│
├── 📄 requirements.txt          # Python dependencies
├── 📄 README.md                 # Full documentation
├── 📄 QUICKSTART.md             # Quick start guide
├── 📄 DEMO_EXAMPLES.md          # Test examples
├── 📄 PROJECT_STRUCTURE.md      # This file
└── 📄 test_system.py            # System testing script
```

---

## 🔍 Detailed File Descriptions

### Core Application Files

#### `app.py` (Main Application)
**Purpose**: Streamlit web interface for the intent prediction system

**Key Features**:
- Interactive UI with text, audio, and vision inputs
- Real-time prediction display
- Confidence scores and visualizations
- Modality toggle controls
- Results dashboard

**How to Run**:
```bash
streamlit run app.py
```

**Main Functions**:
- `load_models()`: Loads and caches all AI models
- `main()`: Main application logic and UI rendering

---

#### `text_model.py` (Text Intent Module)
**Purpose**: Classify customer intent from text input

**Technology**: 
- Hugging Face Transformers
- Zero-shot classification with DistilBART/BERT

**Key Class**: `TextIntentModel`

**Methods**:
- `__init__()`: Initialize the text classification pipeline
- `predict(text)`: Predict intent from text input

**Input**: String (customer message)

**Output**: 
- Dictionary of intent scores
- Primary intent label
- Confidence score

**Example**:
```python
from text_model import TextIntentModel

model = TextIntentModel()
scores, intent, conf = model.predict("I need help with my order")
# Output: intent="Inquiry", conf=0.85
```

---

#### `audio_model.py` (Audio Emotion Module)
**Purpose**: Detect emotion from voice/audio input

**Technology**:
- Wav2Vec2 (Facebook AI)
- Audio classification pipeline
- Librosa for audio processing

**Key Class**: `AudioEmotionModel`

**Methods**:
- `__init__()`: Initialize Wav2Vec2 pipeline
- `predict(audio_file)`: Predict emotion from audio
- `extract_features(audio_bytes)`: Extract MFCC features (optional)

**Input**: Audio file (.wav, .mp3) or file-like object

**Output**:
- Emotion label (angry, happy, sad, fear, neutral, etc.)
- Confidence score

**Supported Emotions**:
- Angry
- Happy
- Sad
- Fear/Fearful
- Neutral/Calm
- Surprise
- Disgust

**Example**:
```python
from audio_model import AudioEmotionModel

model = AudioEmotionModel()
emotion, conf = model.predict("audio.wav")
# Output: emotion="angry", conf=0.92
```

---

#### `vision_model.py` (Facial Emotion Module)
**Purpose**: Detect emotion from facial expressions

**Technology**:
- Vision Transformer (ViT)
- OpenCV for face detection
- Haar Cascade classifier

**Key Class**: `VisionEmotionModel`

**Methods**:
- `__init__()`: Initialize ViT and face detector
- `detect_face(image)`: Detect faces in image
- `predict(image)`: Predict emotion from largest face

**Input**: PIL Image or numpy array (RGB)

**Output**:
- Emotion label
- Confidence score
- Annotated image with bounding box

**Face Detection**:
- Uses Haar Cascade for face detection
- Processes largest face if multiple detected
- Returns None if no face found

**Example**:
```python
from vision_model import VisionEmotionModel
from PIL import Image

model = VisionEmotionModel()
img = Image.open("face.jpg")
emotion, conf, annotated = model.predict(img)
# Output: emotion="happy", conf=0.88
```

---

#### `fusion.py` (Multimodal Fusion Module)
**Purpose**: Combine predictions from multiple modalities

**Key Features**:
- Adaptive weight redistribution
- Confidence-based fusion
- Emotion-to-intent mapping
- Action recommendation

**Key Functions**:
- `fuse_multimodal()`: Main fusion function
- `map_emotion_to_intent_probs()`: Convert emotion to intent probabilities
- `normalize()`: Normalize probability distributions

**Fusion Strategy**:
1. Convert all inputs to intent probability vectors
2. Apply modality-specific weights (Text: 50%, Audio: 30%, Vision: 20%)
3. Dynamically redistribute weights if modalities are missing
4. Weighted average of probability vectors
5. Select highest probability as final intent

**Input**:
- `text_probs`: Dict of intent scores from text model
- `audio_emotion`: Tuple (emotion_label, confidence)
- `vision_emotion`: Tuple (emotion_label, confidence)

**Output**:
- Final intent label
- Final confidence score
- All intent scores (dict)
- Recommended action

**Example**:
```python
from fusion import fuse_multimodal

text_probs = {"Inquiry": 0.7, "Complaint": 0.2, ...}
audio_emotion = ("calm", 0.85)
vision_emotion = ("happy", 0.90)

intent, conf, scores, action = fuse_multimodal(
    text_probs=text_probs,
    audio_emotion=audio_emotion,
    vision_emotion=vision_emotion
)
# Output: intent="Inquiry", conf=0.82, action="Normal routing"
```

---

#### `config.py` (Configuration Module)
**Purpose**: Centralized configuration for all models and settings

**Configurable Settings**:
- Model names and paths
- Fusion weights
- Intent classes
- Emotion-to-intent mapping
- Action recommendation rules
- UI settings
- Performance options

**Key Configurations**:
```python
TEXT_MODEL = {"model_name": "valhalla/distilbart-mnli-12-3", ...}
AUDIO_MODEL = {"model_name": "ehcalabres/wav2vec2-...", ...}
VISION_MODEL = {"model_name": "dima806/facial_emotions_...", ...}
FUSION_WEIGHTS = {"text": 0.5, "audio": 0.3, "vision": 0.2}
```

**Helper Functions**:
- `get_action_for_intent()`: Determine action from intent and confidence
- `validate_config()`: Validate configuration settings

---

### Testing and Documentation Files

#### `test_system.py` (Testing Script)
**Purpose**: Verify installation and test individual modules

**Test Functions**:
- `test_imports()`: Check if all packages are installed
- `test_text_model()`: Test text classification
- `test_fusion()`: Test fusion logic

**How to Run**:
```bash
python test_system.py
```

**Expected Output**:
```
✅ All packages imported successfully!
✅ Text model loaded successfully
✅ Fusion successful
✅ BASIC TESTS PASSED!
```

---

#### `requirements.txt` (Dependencies)
**Purpose**: List all Python package dependencies

**Key Packages**:
- `streamlit`: Web UI framework
- `torch`: Deep learning backend
- `transformers`: Hugging Face models
- `opencv-python`: Computer vision
- `librosa`: Audio processing
- `numpy`, `pandas`: Data manipulation

**Installation**:
```bash
pip install -r requirements.txt
```

---

#### `README.md` (Full Documentation)
**Purpose**: Comprehensive project documentation

**Sections**:
- Features overview
- Installation instructions
- Usage guide
- Technical details
- Troubleshooting
- Academic/viva preparation

---

#### `QUICKSTART.md` (Quick Start Guide)
**Purpose**: Fast-track guide to get started

**Sections**:
- 3-step setup
- First-time usage tips
- Common issues and solutions
- Demo checklist

---

#### `DEMO_EXAMPLES.md` (Test Examples)
**Purpose**: Sample inputs for testing

**Contents**:
- Text examples for each intent class
- Audio testing suggestions
- Vision/facial testing tips
- Multimodal scenarios
- Expected outputs

---

#### `PROJECT_STRUCTURE.md` (This File)
**Purpose**: Detailed explanation of all project files

---

## 🔄 Data Flow

```
User Input (Text/Audio/Image)
        ↓
┌───────┴───────┬───────────┬──────────┐
│               │           │          │
Text Model   Audio Model  Vision Model
│               │           │          │
Intent Probs  Emotion    Emotion
│               │           │          │
└───────┬───────┴───────────┴──────────┘
        ↓
  Fusion Module
        ↓
┌───────┴────────┐
│                │
Final Intent   Action
Confidence     Recommendation
│                │
└───────┬────────┘
        ↓
   Display Results
```

---

## 🎯 Module Dependencies

```
app.py
├── text_model.py
│   └── transformers
├── audio_model.py
│   ├── transformers
│   └── librosa
├── vision_model.py
│   ├── transformers
│   └── opencv-python
└── fusion.py
    └── numpy

config.py (standalone)
test_system.py (uses all modules)
```

---

## 💾 Model Storage

After first run, models are cached in:
```
~/.cache/huggingface/
```

**Total Size**: ~1-2 GB

**Models Downloaded**:
1. Text: `valhalla/distilbart-mnli-12-3` (~300 MB)
2. Audio: `ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition` (~500 MB)
3. Vision: `dima806/facial_emotions_image_detection` (~300 MB)

---

## 🚀 Execution Order

### For Normal Use:
1. Run `pip install -r requirements.txt`
2. Run `streamlit run app.py`
3. Use the web interface

### For Testing:
1. Run `pip install -r requirements.txt`
2. Run `python test_system.py`
3. If tests pass, run `streamlit run app.py`

### For Development:
1. Modify `config.py` for settings
2. Edit individual model files as needed
3. Test with `test_system.py`
4. Run full app with `streamlit run app.py`

---

## 📝 Code Style

- **Language**: Python 3.9+
- **Style**: PEP 8 compliant
- **Documentation**: Docstrings for all classes and functions
- **Comments**: Inline comments for complex logic
- **Modularity**: Separate files for each component

---

## 🎓 For Academic Understanding

### Key Concepts Demonstrated:

1. **Multimodal Learning**: Combining text, audio, and vision
2. **Transfer Learning**: Using pre-trained models
3. **Zero-Shot Classification**: Classifying without task-specific training
4. **Adaptive Systems**: Dynamic weight adjustment
5. **Real-Time Inference**: Fast prediction for production use

### Files to Study for Viva:

1. **`fusion.py`**: Understand multimodal fusion logic
2. **`text_model.py`**: Zero-shot classification approach
3. **`config.py`**: Emotion-to-intent mapping heuristics
4. **`app.py`**: System integration and UI

---

**Last Updated**: 2026-02-11
**Version**: 1.0
**Author**: AI Intent Prediction System
