import streamlit as st
import numpy as np
from PIL import Image
import io
import time
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import os
import pandas as pd
from moviepy import VideoFileClip

# Import our custom modules (moved to lazy loading to speed up startup)
# from text_model import TextIntentModel
# from audio_model import AudioEmotionModel
# from vision_model import VisionEmotionModel
from fusion import fuse_multimodal, INTENT_CLASSES

def extract_audio_from_video(video_bytes, file_ext):
    """Extract audio from video file bytes and return as audio file path."""
    try:
        # Create temp video file
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        tfile.write(video_bytes)
        tfile.close()
        
        video_path = tfile.name
        audio_path = video_path.replace(file_ext, ".wav")
        
        # Load video and extract audio
        video = VideoFileClip(video_path)
        if video.audio is None:
            return None, "No audio track found in video"
            
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()
        
        # Clean up video file
        try:
            os.remove(video_path)
        except:
            pass
            
        return audio_path, None
    except Exception as e:
        return None, str(e)

# Page configuration
st.set_page_config(
    page_title="AI Intent Prediction System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# STUNNING CUSTOM CSS - Premium Glassmorphism Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;600&display=swap');
    
    :root {
        --primary: #6366f1;
        --primary-glow: rgba(99, 102, 241, 0.5);
        --secondary: #a855f7;
        --bg-dark: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
        --text-main: #f8fafc;
        --text-dim: #94a3b8;
    }

    /* Global Styles */
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a 50%, #020617);
        color: var(--text-main);
        font-family: 'Outfit', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* Main Header */
    .main-header {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        padding: 3rem 2rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 0deg, transparent, var(--primary), transparent 30%);
        animation: rotate 10s linear infinite;
        opacity: 0.1;
        z-index: -1;
    }

    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .main-header h1 {
        background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        margin: 0;
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));
    }
    
    .main-header p {
        color: var(--text-dim);
        font-size: 1.25rem;
        margin-top: 1rem;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.2em;
    }

    /* Card/Module Styles */
    .card {
        background: var(--card-bg);
        backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .card:hover {
        transform: translateY(-8px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 20px rgba(99, 102, 241, 0.1);
    }
    
    /* Input Elements styling */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 1.1rem !important;
    }

    /* Prediction Result Box */
    .result-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 24px;
        position: relative;
        text-align: center;
        margin: 2rem 0;
        overflow: hidden;
    }
    
    .result-box::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }

    /* Intent Badges - Glow version */
    .intent-badge {
        display: inline-block;
        padding: 0.6rem 2rem;
        border-radius: 100px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.9rem;
        margin-top: 1.5rem;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .badge-inquiry { background: rgba(99, 102, 241, 0.2); color: #818cf8; box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); }
    .badge-complaint { background: rgba(244, 63, 94, 0.2); color: #fb7185; box-shadow: 0 0 20px rgba(244, 63, 94, 0.3); }
    .badge-escalation { background: rgba(234, 179, 8, 0.2); color: #facc15; box-shadow: 0 0 20px rgba(234, 179, 8, 0.3); }
    .badge-distress { background: rgba(236, 72, 153, 0.2); color: #f472b6; box-shadow: 0 0 20px rgba(236, 72, 153, 0.3); }
    .badge-neutral { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; box-shadow: 0 0 20px rgba(148, 163, 184, 0.3); }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background: #020617;
        border-right: 1px solid var(--glass-border);
    }
    
    .stCheckbox label {
        color: var(--text-dim) !important;
        font-weight: 500 !important;
    }
    
    /* Button Hover Effects */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 15px 25px rgba(99, 102, 241, 0.5) !important;
        opacity: 0.9;
    }
    /* Result Typography */
    .intent-label {
        font-size: 0.9rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin-bottom: 0.5rem;
    }
    
    .intent-value {
        font-size: 4rem;
        margin: 0;
        background: white;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Action Card styling */
    .action-card {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 2rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .action-icon {
        background: rgba(99, 102, 241, 0.1);
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for models (load on demand)
@st.cache_resource
def load_text_engine():
    """Load text model lazily."""
    from text_model import TextIntentModel
    return TextIntentModel()

@st.cache_resource
def load_audio_engine():
    """Load audio model lazily."""
    from audio_model import AudioEmotionModel
    return AudioEmotionModel()

@st.cache_resource
def load_vision_engine():
    """Load vision model lazily."""
    from vision_model import VisionEmotionModel
    return VisionEmotionModel()

def get_session_history():
    """Get or initialize session history."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    return st.session_state.history

def add_to_history(text_input, audio_file, vision_input, intent, confidence, action):
    """Add a prediction to history."""
    timestamp = time.strftime("%H:%M:%S")
    
    # Determine input type
    inputs = []
    if text_input: inputs.append("Text")
    if audio_file: inputs.append("Audio")
    if vision_input: inputs.append("Vision")
    input_type = " + ".join(inputs) if inputs else "None"
    
    entry = {
        "Time": timestamp,
        "Input Type": input_type,
        "Text Preview": text_input[:30] + "..." if text_input else "N/A",
        "Predicted Intent": intent,
        "Confidence": f"{confidence:.1%}",
        "Action": action
    }
    st.session_state.history.insert(0, entry) # Add to top

def create_confidence_gauge(confidence, intent):
    """Create a high-end confidence gauge."""
    colors = {
        "Inquiry": "#6366f1",
        "Complaint": "#f43f5e",
        "Escalation": "#eab308",
        "Distress": "#db2777",
        "Neutral": "#94a3b8"
    }
    color = colors.get(intent, "#6366f1")
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confidence * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        number = {'suffix': "%", 'font': {'size': 60, 'color': 'white', 'family': 'Outfit'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#334155"},
            'bar': {'color': color},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': 'rgba(255, 255, 255, 0.02)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 2},
                'thickness': 0.8,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=30, b=30),
        height=280
    )
    
    return fig

def create_intent_distribution(all_scores):
    """Create a beautiful bar chart for intent distribution."""
    intents = list(all_scores.keys())
    scores = [all_scores[i] * 100 for i in intents]
    
    colors_map = {
        "Inquiry": "#6366f1",
        "Complaint": "#f43f5e",
        "Escalation": "#eab308",
        "Distress": "#db2777",
        "Neutral": "#94a3b8"
    }
    colors = [colors_map.get(i, "#6366f1") for i in intents]
    
    fig = go.Figure(data=[
        go.Bar(
            x=intents,
            y=scores,
            marker=dict(
                color=colors,
                line=dict(color='rgba(255,255,255,0.2)', width=1)
            ),
            text=[f"{s:.1f}%" for s in scores],
            textposition='outside',
            textfont=dict(size=14, color='white', family='Outfit')
        )
    ])
    
    fig.update_layout(
        title={
            'text': "PROBABILITY SPECTRUM",
            'font': {'size': 20, 'color': '#94a3b8', 'family': 'Outfit'}
        },
        xaxis=dict(
            tickfont=dict(size=12, color='#94a3b8'),
            gridcolor='rgba(255,255,255,0.05)'
        ),
        yaxis=dict(
            tickfont=dict(size=12, color='#94a3b8'),
            gridcolor='rgba(255,255,255,0.05)',
            range=[0, max(scores) * 1.3]
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        height=350,
        showlegend=False
    )
    
    return fig

def main():
    # Header with Premium UI
    st.markdown("""
    <div class="main-header">
        <h1>NEURAL INTENT CORE</h1>
        <p>Adaptive Multimodal Fusion Framework v2.1</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Models will be loaded lazily below as needed
    text_model = None
    audio_model = None
    vision_model = None
    
    # Fixed variables since we are unifying everything
    use_text = True
    use_audio = True
    use_vision = True

    # Sidebar for system status & settings
    with st.sidebar:
        st.markdown("## ⚙️ SYSTEM CONTROL")
        st.markdown("---")
        
        use_debug = st.checkbox("🐞 Debug Mode", value=False, help="Show detailed fusion logic")
        
        st.markdown("---")
        st.markdown("### 📊 SYSTEM ARCHITECTURE")
        st.info("""
        **CORE ENGINES:**
        - 🤖 BERT/DistilBART (Textual)
        - 🎵 Wav2Vec2 (Acoustic)
        - 👁️ Vision Transformer (Optical)
        """)
        
        st.markdown("---")
        st.markdown("### ⚖️ ADAPTIVE BIAS control")
        with st.expander("Modality Importance Tuning"):
            w_text = st.slider("Text Bias", 0.0, 1.0, 0.45, 0.05)
            w_audio = st.slider("Audio Bias", 0.0, 1.0, 0.35, 0.05)
            w_vision = st.slider("Vision Bias", 0.0, 1.0, 0.20, 0.05)
            
            total = w_text + w_audio + w_vision
            if total > 0:
                st.caption(f"Current Ratio: T:{w_text/total:.1%} | A:{w_audio/total:.1%} | V:{w_vision/total:.1%}")

    
    # Main content area with dual-column dashboard
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 📥 UNIVERSAL NEURAL TERMINAL")
        
        # Performance Mode Selector for hardware isolation
        input_mode = st.pills(
            "Select Processing Modality",
            ["Textual", "Acoustic", "Optical", "Media Upload", "Live Unified"],
            selection_mode="single",
            default="Textual",
            key="modality_pills"
        )
        
        st.markdown("---")
        
        text_input = ""
        audio_file = None
        image_input = None
        detected_modalities = []

        if input_mode == "Textual":
            st.markdown("### ✍️ TEXT CONSOLE")
            text_input = st.text_area(
                "Neural Command Input",
                placeholder="Type message for analysis...",
                height=150,
                key="p_text_input"
            )
            if text_input: detected_modalities.append("📝 TEXTUAL")

        elif input_mode == "Acoustic":
            st.markdown("### 🎙️ ACOUSTIC SENSOR")
            st.info("Direct microphone uplink activated.")
            try:
                from audio_recorder_streamlit import audio_recorder
                live_audio_bytes = audio_recorder(text="Record Voice", icon_size="2x", key="p_mic_rec")
                if live_audio_bytes:
                    audio_file = io.BytesIO(live_audio_bytes)
                    audio_file.name = "live_audio.wav"
                    detected_modalities.append("🎤 LIVE ACOUSTIC")
            except Exception as e:
                st.error("Audio hardware unreachable.")

        elif input_mode == "Optical":
            st.markdown("### 👁️ OPTICAL SENSOR")
            st.info("Direct camera-only uplink activated.")
            live_vision_img = st.camera_input("Capture Facial Vector", key="p_cam_inp")
            if live_vision_img:
                image_input = Image.open(live_vision_img)
                detected_modalities.append("📷 LIVE OPTICAL")

        elif input_mode == "Media Upload":
            st.markdown("### 📁 MEDIA UPLINK")
            uploaded_media = st.file_uploader(
                "Drop Media Files",
                type=['wav', 'mp3', 'm4a', 'flac', 'ogg', 'mp4', 'avi', 'mov', 'png', 'jpg', 'jpeg'],
                key="p_upload_terminal",
                accept_multiple_files=True
            )
            if uploaded_media:
                for file in uploaded_media:
                    ext = os.path.splitext(file.name)[1].lower()
                    if ext in ['.wav', '.mp3', '.m4a', '.flac', '.ogg']:
                        audio_file = file
                        detected_modalities.append(f"🎧 AUDIO ({file.name})")
                    elif ext in ['.png', '.jpg', '.jpeg']:
                        image_input = Image.open(file)
                        detected_modalities.append(f"👁️ IMAGE ({file.name})")
                    elif ext in ['.mp4', '.avi', '.mov']:
                        with st.spinner("Extracting stream..."):
                            extracted_path, _ = extract_audio_from_video(file.read(), ext)
                            if extracted_path:
                                with open(extracted_path, 'rb') as f:
                                    audio_file = io.BytesIO(f.read())
                                    audio_file.name = "vid_stream.wav"
                                detected_modalities.append(f"🎬 VIDEO-AUDIO ({file.name})")

        elif input_mode == "Live Unified":
            st.markdown("### 🔴 MULTIMODAL LIVE SESSION")
            st.warning("Synchronized sensor array: Camera and Microphone will activate together.")
            u_col1, u_col2 = st.columns(2)
            with u_col1:
                from audio_recorder_streamlit import audio_recorder
                u_audio = audio_recorder(text="Mic Sync", icon_size="2x", key="p_u_mic")
                if u_audio:
                    audio_file = io.BytesIO(u_audio)
                    audio_file.name = "sync_audio.wav"
                    detected_modalities.append("🎤 SYNC AUDIO")
            with u_col2:
                u_img = st.camera_input("Cam Sync", key="p_u_cam")
                if u_img:
                    image_input = Image.open(u_img)
                    detected_modalities.append("📷 SYNC VISION")

        # DYNAMIC VALIDATION FEEDBACK
        if detected_modalities:
            st.markdown("---")
            st.markdown("### 🧬 SENSORY VALIDATION")
            for mod in detected_modalities:
                st.markdown(f'<div style="background: rgba(99,102,241,0.1); border-left: 3px solid var(--primary); padding: 5px 15px; margin-bottom: 5px; border-radius: 4px;">✅ {mod} detected</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 🧠 NEURAL SYNTHESIS")
        
        # Predict button with better styling
        predict_btn = st.button("🚀 PREDICT INTENT", type="primary", use_container_width=True)
        
        if predict_btn:
            # Check if at least one input is provided
            if not any([text_input, audio_file, image_input]):
                st.warning("⚠️ Please provide at least one input (Text, Audio, or Image)!")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Storage for modality results
            text_probs = None
            audio_emotion = None
            vision_emotion = None
            
            # Unified Processing Queue
            active_signals = []
            
            # 1. Process Text Component
            if text_input:
                status_text.text("📡 INTERCEPTING TEXT STREAM...")
                progress_bar.progress(20)
                try:
                    # Lazy load text model if needed
                    if text_model is None:
                        with st.spinner("🔄 Loading Text Engine..."):
                            text_model = load_text_engine()
                    
                    scores, primary, conf = text_model.predict(text_input)
                    text_probs = scores
                    active_signals.append(f"Text: {primary}")
                except Exception as e:
                    st.error(f"Text sequence error: {e}")
            
            # 2. Process Audio Component
            if audio_file:
                status_text.text("🎙️ DECODING ACOUSTIC SIGNALS...")
                progress_bar.progress(50)
                try:
                    # Lazy load audio model if needed
                    if audio_model is None:
                        with st.spinner("🔄 Loading Audio Engine..."):
                            audio_model = load_audio_engine()
                            
                    emotion_label, emotion_conf = audio_model.predict(audio_file)
                    if emotion_label:
                        audio_emotion = (emotion_label, emotion_conf)
                        active_signals.append(f"Audio: {emotion_label}")
                except Exception as e:
                    st.error(f"Acoustic processing error: {e}")
            
            # 3. Process Vision Component
            if image_input:
                status_text.text("👁️ ANALYZING OPTICAL VECTORS...")
                progress_bar.progress(75)
                try:
                    # Lazy load vision model if needed
                    if vision_model is None:
                        with st.spinner("🔄 Loading Vision Engine..."):
                            vision_model = load_vision_engine()
                            
                    emotion_label, emotion_conf, annotated_img = vision_model.predict(image_input)
                    if emotion_label:
                        vision_emotion = (emotion_label, emotion_conf)
                        active_signals.append(f"Vision: {emotion_label}")
                        if use_debug:
                            st.image(annotated_img, caption="Vector Overlay", use_container_width=True)
                    else:
                        st.warning("⚠️ OPTICAL LOCK FAILED: Face not detected")
                except Exception as e:
                    st.error(f"Vision computation error: {e}")
            
            # High-Level Convergence Status
            if active_signals:
                st.info(f"🧬 SIGNAL CONVERGENCE: {' + '.join(active_signals)}")
            
            # Fusion
            status_text.text("🔄 Fusing multimodal data...")
            progress_bar.progress(90)
            
            try:
                # Create weights dictionary
                fusion_weights = {
                    'text': w_text,
                    'audio': w_audio,
                    'vision': w_vision
                }
                
                final_intent, final_conf, all_scores, action = fuse_multimodal(
                    text_probs=text_probs,
                    audio_emotion=audio_emotion,
                    vision_emotion=vision_emotion,
                    weights=fusion_weights
                )
                
                # Add to history
                add_to_history(
                    text_input if use_text else None, 
                    "Audio File" if use_audio and audio_file else None, 
                    "Vision Input" if use_vision and image_input else None,
                    final_intent, 
                    final_conf, 
                    action
                )
            
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # Display stunning results
                st.markdown("---")
                
                # Main result card
                # Display Stunning Premium Results
                badge_class = f"badge-{final_intent.lower()}"
                st.markdown(f"""
<div class="result-box">
<div class="intent-label">System Analysis Result</div>
<h2 class="intent-value">{final_intent}</h2>
<div class="intent-badge {badge_class}">Confidence: {final_conf:.1%}</div>
<div class="action-card">
<div class="action-icon">📋</div>
<div style="text-align: left;">
<div style="font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.1em;">Recommended Action</div>
<div style="font-size: 1.25rem; font-weight: 600; color: white;">{action}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
                
                # Confidence gauge
                st.plotly_chart(create_confidence_gauge(final_conf, final_intent), use_container_width=True)
                
                # Intent distribution chart
                st.plotly_chart(create_intent_distribution(all_scores), use_container_width=True)
                
                # Detailed Analysis breakdown
                st.markdown('<div style="margin-top: 3rem;">', unsafe_allow_html=True)
                st.markdown("### 🧬 VECTOR ANALYSIS")
                
                cols = st.columns(len(INTENT_CLASSES))
                for idx, intent in enumerate(INTENT_CLASSES):
                    with cols[idx]:
                        score = all_scores.get(intent, 0.0)
                        # Color based on intent for intensity
                        st.metric(intent.upper(), f"{score:.1%}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Debug Info (Only in debug mode)
                if use_debug:
                    st.markdown("---")
                    st.warning("🐞 **CORE DEBUG TRACE**")
                    with st.expander("Neural Weights & Probabilities", expanded=True):
                        st.json({
                            "Text": text_probs if text_probs else "OFF",
                            "Audio": audio_emotion if audio_emotion else "OFF",
                            "Vision": vision_emotion if vision_emotion else "OFF",
                            "System_Fusion": all_scores
                        })
                
            except Exception as e:
                st.error(f"❌ FUSION COLLAPSE: {e}")
                import traceback
                st.code(traceback.format_exc())
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    # LOGS - High performance table
    st.markdown("---")
    st.markdown("### �️ TRANSACTION LOGS")
    
    history = get_session_history()
    if history:
        df = pd.DataFrame(history)
        st.dataframe(
            df, 
            use_container_width=True,
            hide_index=True
        )
        
        # Download button with premium feel
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 EXPORT ANALYTICS (CSV)",
            csv,
            "neural_intent_report.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("System stand-by. No active logs detected.")

if __name__ == "__main__":
    main()
