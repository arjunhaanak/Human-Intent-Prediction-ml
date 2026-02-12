# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```
⏱️ **Time**: 5-10 minutes (downloads ~500MB of packages)

### Step 2: Test the System (Optional but Recommended)
```bash
python test_system.py
```
This will verify that all packages are installed correctly.

### Step 3: Run the Application
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`

---

## 📱 First Time Usage

### On First Launch:
1. The app will download AI models (~1-2 GB total)
2. This happens automatically and only once
3. Models are cached for future use
4. **Be patient** - first prediction takes 30-60 seconds

### Quick Test:
1. ✅ Enable "Text Input" in sidebar
2. ❌ Disable "Audio" and "Vision" for now
3. Type: "I am very frustrated with your service!"
4. Click "Predict Intent"
5. Expected result: **Complaint** or **Escalation**

---

## 🎯 Using Each Modality

### 📝 Text Input
- **Always available** - no setup needed
- Most accurate for specific intent
- Try the examples in `DEMO_EXAMPLES.md`

### 🎤 Audio Input
- Upload `.wav` or `.mp3` files
- Works best with clear speech
- Detects emotional tone (angry, happy, sad, etc.)
- **Tip**: Record yourself saying the text examples

### 📷 Facial Emotion
- Use webcam or upload image
- Face must be clearly visible
- Works best with frontal face view
- **Tip**: Make exaggerated expressions for testing

---

## 💡 Tips for Best Results

### For Accurate Predictions:
1. **Use multiple modalities** - More data = better accuracy
2. **Be consistent** - Align text, tone, and expression
3. **Clear inputs** - Good audio quality, visible face, coherent text

### For Testing Fusion:
1. **Try conflicting inputs** - Happy text + angry voice
2. **Observe confidence scores** - Lower when signals conflict
3. **Test with missing modalities** - System adapts automatically

---

## 🐛 Common Issues & Solutions

### Issue: "Model loading failed"
**Solution**: Check internet connection, models need to download

### Issue: "No face detected"
**Solution**: 
- Ensure face is clearly visible
- Try better lighting
- Face camera directly
- Upload a different image

### Issue: "Audio file error"
**Solution**:
- Convert to .wav format
- Ensure file is not corrupted
- Try a different audio file

### Issue: "Slow predictions"
**Solution**:
- First prediction is always slow (model loading)
- Subsequent predictions are faster
- Vision model is slowest - disable if not needed

### Issue: "Low confidence scores"
**Solution**:
- This is normal for conflicting inputs
- Try more aligned inputs (e.g., angry text + angry voice)
- Single modality may give higher confidence

---

## 📊 Understanding Results

### Intent Classes:
- **Inquiry**: Questions, information seeking
- **Complaint**: Dissatisfaction, problems
- **Escalation**: Demands, urgency
- **Distress**: Fear, urgent help needed
- **Neutral**: General conversation

### Confidence Scores:
- **> 80%**: Very confident, aligned inputs
- **60-80%**: Confident, mostly aligned
- **40-60%**: Moderate, some conflict
- **< 40%**: Low, conflicting signals

### Recommended Actions:
- **Normal routing**: Standard customer service
- **Priority handling**: Faster response needed
- **Automatic escalation**: Route to supervisor
- **Immediate Human Agent**: Urgent human intervention

---

## 🎓 For Viva/Demonstration

### Key Points to Explain:
1. **Multimodal Fusion**: How we combine text, audio, and vision
2. **Adaptive Weighting**: System works even if modalities are missing
3. **Transfer Learning**: Using pre-trained models (BERT, Wav2Vec2, ViT)
4. **Real-world Application**: Customer service automation

### Demo Flow:
1. Start with text-only example
2. Add audio to show fusion
3. Add vision to show full multimodal
4. Show conflicting inputs to demonstrate adaptive fusion
5. Explain the confidence scores and action recommendations

### Questions to Prepare For:
- Why these specific models?
- How does emotion map to intent?
- What if modalities conflict?
- How to improve accuracy?
- Real-world deployment considerations?

---

## 📁 Project Files Overview

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit UI |
| `text_model.py` | BERT intent classification |
| `audio_model.py` | Wav2Vec2 emotion detection |
| `vision_model.py` | ViT facial emotion detection |
| `fusion.py` | Multimodal fusion logic |
| `test_system.py` | Testing script |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |
| `DEMO_EXAMPLES.md` | Test examples |
| `QUICKSTART.md` | This file |

---

## ✅ Checklist Before Demo

- [ ] All dependencies installed
- [ ] Test script runs successfully
- [ ] App launches without errors
- [ ] Tested text-only prediction
- [ ] Tested with audio (if using)
- [ ] Tested with webcam/image (if using)
- [ ] Prepared example inputs
- [ ] Understand fusion logic
- [ ] Can explain confidence scores
- [ ] Ready to answer questions

---

## 🆘 Need Help?

1. Check error messages in terminal
2. Review `README.md` for detailed info
3. Run `test_system.py` to diagnose issues
4. Check `DEMO_EXAMPLES.md` for test cases

---

**Ready to start? Run:**
```bash
streamlit run app.py
```

**Good luck with your demo! 🎉**
