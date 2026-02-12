# Demo Examples for Testing

This file contains example inputs you can use to test the application.

## Text Examples

### Example 1: Inquiry
```
I would like to know more about your product features and pricing options.
```
**Expected**: Inquiry, Normal routing

### Example 2: Complaint
```
I am very disappointed with the quality of service. This is unacceptable!
```
**Expected**: Complaint, Priority handling

### Example 3: Escalation
```
I demand to speak with your manager immediately! This has gone on long enough!
```
**Expected**: Escalation, Automatic escalation

### Example 4: Distress
```
I'm really scared and don't know what to do. Please help me urgently!
```
**Expected**: Distress, Immediate Human Agent

### Example 5: Neutral
```
Thank you for the information. Have a nice day.
```
**Expected**: Neutral, Normal routing

## Audio Testing

If you don't have audio files, you can:

1. **Record your own**: Use Windows Voice Recorder or any audio recording software
2. **Use text-to-speech**: Convert the text examples above to speech
3. **Download samples**: Search for "emotion audio samples" online

### Recommended Audio Emotions to Test:
- **Angry tone**: For Complaint/Escalation testing
- **Calm/Happy tone**: For Inquiry/Neutral testing
- **Fearful/Sad tone**: For Distress testing

## Vision/Facial Testing

For facial emotion testing:

1. **Use webcam**: Click "capture from webcam" in the app
2. **Upload images**: Take selfies with different expressions
3. **Test expressions**:
   - Angry face → Should map to Complaint/Escalation
   - Happy face → Should map to Inquiry/Neutral
   - Sad/Fearful face → Should map to Distress
   - Neutral face → Should map to Neutral/Inquiry

## Multimodal Testing Scenarios

### Scenario 1: Frustrated Customer
- **Text**: "This is completely unacceptable! I want a refund now!"
- **Audio**: Angry, loud tone
- **Vision**: Angry facial expression
- **Expected**: High confidence Escalation/Complaint

### Scenario 2: Happy Inquiry
- **Text**: "I'm interested in learning more about your services"
- **Audio**: Cheerful, calm tone
- **Vision**: Smiling face
- **Expected**: High confidence Inquiry

### Scenario 3: Distressed Customer
- **Text**: "I'm really worried and need help urgently"
- **Audio**: Fearful, shaky tone
- **Vision**: Worried/fearful expression
- **Expected**: High confidence Distress

### Scenario 4: Conflicting Signals (Tests Adaptive Fusion)
- **Text**: "Everything is fine, thank you" (Neutral)
- **Audio**: Angry tone (Complaint)
- **Vision**: Not provided
- **Expected**: System should balance text and audio, likely Complaint with moderate confidence

## Testing Tips

1. **Start Simple**: Test with text only first
2. **Add Modalities**: Gradually enable audio and vision
3. **Check Confidence**: Higher confidence = more aligned modalities
4. **Test Edge Cases**: Try conflicting inputs to see adaptive fusion
5. **Monitor Performance**: First prediction is slower (model loading)

## Troubleshooting Test Cases

If predictions seem off:

1. **Check input quality**: Clear audio, visible face, coherent text
2. **Verify modality toggles**: Ensure correct modalities are enabled
3. **Review console output**: Check for error messages
4. **Test individually**: Disable other modalities to isolate issues

## Expected System Behavior

| Intent | Confidence | Action |
|--------|-----------|--------|
| Inquiry | Any | Normal routing |
| Neutral | Any | Normal routing |
| Complaint | < 60% | Priority handling |
| Complaint | > 60% | Automatic escalation |
| Escalation | < 60% | Priority handling |
| Escalation | > 60% | Automatic escalation |
| Distress | Any | Immediate Human Agent |
