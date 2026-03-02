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
import threading
from concurrent.futures import ThreadPoolExecutor

# Import our custom modules (moved to lazy loading to speed up startup)
# from text_model import TextIntentModel
# from audio_model import AudioEmotionModel
# from vision_model import VisionEmotionModel
from fusion import fuse_multimodal, INTENT_CLASSES

def process_video_input(video_bytes, file_ext):
    """Process video to extract both audio and sample frames for vision analysis."""
    try:
        # Create temp video file
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        tfile.write(video_bytes)
        tfile.close()
        
        video_path = tfile.name
        audio_path = video_path.replace(file_ext, ".wav")
        
        # Load video
        video = VideoFileClip(video_path)
        
        # 1. Extract Audio
        has_audio = False
        if video.audio is not None:
            video.audio.write_audiofile(audio_path, logger=None)
            has_audio = True
            
        # 2. Extract sample frames (e.g., 5 frames spread across the video)
        duration = video.duration
        sample_times = np.linspace(0, duration * 0.9, 5)
        frames = []
        for t in sample_times:
            frame = video.get_frame(t)
            frames.append(frame)
            
        video.close()
        
        # Clean up video file
        try:
            os.remove(video_path)
        except:
            pass
            
        return (audio_path if has_audio else None, frames, None)
    except Exception as e:
        return (None, None, str(e))

# Page configuration
st.set_page_config(
    page_title="NEURAL INTENT CORE | Advanced Multimodal AI",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# STUNNING CUSTOM CSS - Ultimate AI Aesthetic
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');
    
    :root {
        --primary: #6366f1;
        --primary-glow: rgba(99, 102, 241, 0.4);
        --secondary: #a855f7;
        --accent: #00f2ff;
        --bg-dark: #020617;
        --card-bg: rgba(15, 23, 42, 0.6);
        --glass-border: rgba(255, 255, 255, 0.08);
        --text-main: #f8fafc;
        --text-dim: #94a3b8;
    }

    /* Animated Dynamic Background */
    .stApp {
        background: #020617;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0, transparent 50%), 
            radial-gradient(at 50% 100%, rgba(168, 85, 247, 0.15) 0, transparent 50%),
            radial-gradient(at 100% 0%, rgba(0, 242, 255, 0.05) 0, transparent 50%);
        background-attachment: fixed;
        color: var(--text-main);
        font-family: 'Outfit', sans-serif;
    }
    
    /* Entrance Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); filter: blur(10px); }
        to { opacity: 1; transform: translateY(0); filter: blur(0); }
    }
    
    @keyframes glowPulse {
        0% { filter: drop-shadow(0 0 5px var(--primary-glow)); }
        100% { filter: drop-shadow(0 0 15px var(--primary)); }
    }

    .card, .main-header, .result-box, .stMetric, .stPlotlyChart {
        animation: fadeInUp 0.8s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 800 !important;
        letter-spacing: -0.03em;
    }

    /* Main Header - Cyber Deck Design */
    .main-header {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        padding: 4rem 2rem;
        border-radius: 32px;
        text-align: center;
        margin-bottom: 3.5rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(45deg, transparent, rgba(99, 102, 241, 0.05), transparent);
        transform: translateX(-100%);
        animation: scan 3s infinite linear;
    }

    @keyframes scan {
        100% { transform: translateX(100%); }
    }

    .main-header h1 {
        background: linear-gradient(135deg, #fff 30%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem;
        margin: 0;
        line-height: 1;
        letter-spacing: -0.05em;
    }
    
    .main-header p {
        color: var(--accent);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        margin-top: 1.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.4em;
        opacity: 0.8;
    }

    /* Premium Card Design */
    .card {
        background: var(--card-bg);
        backdrop-filter: blur(24px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .card:hover {
        transform: translateY(-5px) scale(1.01);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        background: rgba(30, 41, 59, 0.6);
    }
    
    /* Input Elements styling */
    .stTextArea textarea {
        background: rgba(2, 6, 23, 0.6) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 16px !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1.2rem !important;
        transition: border 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px var(--primary-glow) !important;
    }

    /* Prediction Result Box - Hyperglow */
    .result-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(30px);
        padding: 3rem;
        border-radius: 32px;
        position: relative;
        text-align: center;
        margin: 2rem 0;
        overflow: hidden;
        animation: pulse-border 4s infinite alternate ease-in-out;
    }
    
    @keyframes pulse-border {
        0% { border-color: rgba(99, 102, 241, 0.2); box-shadow: 0 0 20px rgba(99, 102, 241, 0.1); }
        100% { border-color: rgba(168, 85, 247, 0.5); box-shadow: 0 0 40px rgba(168, 85, 247, 0.2); }
    }

    /* Intent Badges */
    .intent-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.75rem 2.5rem;
        border-radius: 100px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.85rem;
        margin-top: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    .badge-inquiry { background: rgba(99, 102, 241, 0.15); color: #818cf8; border-color: rgba(99, 102, 241, 0.3); }
    .badge-complaint { background: rgba(244, 63, 94, 0.15); color: #fb7185; border-color: rgba(244, 63, 94, 0.3); }
    .badge-escalation { background: rgba(234, 179, 8, 0.15); color: #facc15; border-color: rgba(234, 179, 8, 0.3); }
    .badge-distress { background: rgba(236, 72, 153, 0.15); color: #f472b6; border-color: rgba(236, 72, 153, 0.3); }
    .badge-neutral { background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border-color: rgba(148, 163, 184, 0.3); }

    /* Button Styling - Ultimate Gradient */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #d946ef 100%) !important;
        background-size: 200% auto !important;
        border: none !important;
        border-radius: 16px !important;
        color: white !important;
        font-weight: 800 !important;
        padding: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.15em !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4) !important;
    }
    
    .stButton > button:hover {
        background-position: right center !important;
        transform: scale(1.02) translateY(-2px) !important;
        box-shadow: 0 20px 30px -10px rgba(99, 102, 241, 0.6) !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(2, 6, 23, 0.5); }
    ::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary-glow); }

    /* Metric Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        font-family: 'Outfit', sans-serif !important;
        color: white !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: var(--accent) !important;
    }

    /* AI Insight Box */
    .insight-text {
        font-style: italic;
        border-left: 2px solid var(--accent);
        padding-left: 1rem;
        margin: 1rem 0;
        color: #e2e8f0;
    }

    /* Mobile Responsiveness & PWA Enhancements */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2.2rem; }
        .main-header { padding: 2rem 1rem; margin-bottom: 2rem; }
        .intent-value { font-size: 2.5rem; }
        .card { padding: 1.5rem; }
        .result-box { padding: 1.5rem; }
    }

    /* Pulse for Status */
    .status-pulse {
        width: 10px; height: 10px;
        background: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
</style>

<!-- PWA & Mobile Meta Tags -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#020617">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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

def create_modality_comparison_chart(modality_probs, all_scores):
    """Create a grouped bar chart comparing modality predictions."""
    fig = go.Figure()
    
    mod_colors = {
        'text': '#6366f1',   # Indigo
        'audio': '#a855f7',  # Purple
        'vision': '#ec4899', # Pink
        'fused': '#ffffff'   # White/Glow
    }
    
    # Add bars for each modality
    for mod, probs in modality_probs.items():
        fig.add_trace(go.Bar(
            name=mod.capitalize(),
            x=INTENT_CLASSES,
            y=[p * 100 for p in probs],
            marker_color=mod_colors.get(mod, '#94a3b8'),
            opacity=0.7
        ))
    
    # Add the final fused result as a special line/outline or bar
    fig.add_trace(go.Bar(
        name='FUSED (Result)',
        x=INTENT_CLASSES,
        y=[all_scores[c] * 100 for c in INTENT_CLASSES],
        marker=dict(
            color='rgba(255,255,255,0.1)',
            line=dict(color='#ffffff', width=2)
        )
    ))
    
    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#94a3b8")
        ),
        xaxis=dict(tickfont=dict(color='#94a3b8'), gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(title="Confidence %", tickfont=dict(color='#94a3b8'), gridcolor='rgba(255,255,255,0.05)')
    )
    
    return fig

def generate_ai_insight(intent, confidence, modality_probs, text, audio, vision):
    """Generate a pseudo-AI explanation of the decision."""
    if not modality_probs:
        return "System in standby. Provide input for neural analysis."
        
    motives = []
    
    if 'text' in modality_probs:
        text_top = INTENT_CLASSES[np.argmax(modality_probs['text'])]
        motives.append(f"semantically indicates **{text_top}**")
        
    if 'audio' in modality_probs:
        motives.append(f"acoustic signatures reflect **{audio[0]}** emotions")
        
    if 'vision' in modality_probs:
        motives.append(f"optical biometric data mirrors **{vision[0]}**")
        
    if len(motives) > 1:
        primer = "The convergence of signals " + ", and ".join(motives)
    elif len(motives) == 1:
        primer = f"The {list(modality_probs.keys())[0]} input " + motives[0]
    else:
        primer = "Neural synthesis complete"
        
    if confidence > 0.8:
        strength = "highly conclusive"
    elif confidence > 0.5:
        strength = "moderate"
    else:
        strength = "preliminary (divergent signals)"
        
    return f"{primer}. Synthesis is **{strength}**, classifying intent as **{intent}**."

def main():
    # Header with Premium UI
    st.markdown("""
    <div class="main-header">
        <h1>NEURAL <span style="color: var(--primary);">INTENT</span> CORE</h1>
        <p>▷ ADAPTIVE MULTIMODAL SYNTHESIS :: v3.5</p>
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
        
        # NEURAL ENGINE STATUS
        st.markdown("### 🧬 NEURAL ENGINE STATUS")
        
        # Synchronous System Warm-up
        if 'system_ready' not in st.session_state:
            with st.status("🛠️ INITIALIZING NEURAL CORE...", expanded=True) as status:
                st.write("📡 Pre-loading Text Engine (BERT)...")
                load_text_engine()
                st.write("🎙️ Pre-loading Acoustic Engine (Wav2Vec2)...")
                load_audio_engine()
                st.write("👁️ Pre-loading Optical Engine (ViT)...")
                load_vision_engine()
                status.update(label="✅ NEURAL CORE SYNCHRONIZED", state="complete", expanded=False)
            st.session_state.system_ready = True
            st.rerun()

        # Simple status labels (Green Pulse)
        st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 10px; border-radius: 12px; display: flex; align-items: center;">
                <div class="status-pulse"></div>
                <span style="color: #10b981; font-weight: 600; font-size: 0.9rem;">READY: HIGH-SPEED INFERENCE ACTIVE</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        use_debug = st.checkbox("🐞 Debug Mode", value=False, help="Show detailed fusion logic")

        
        st.markdown("---")
        st.markdown("### 📊 SYSTEM ARCHITECTURE")
        st.info("""
        **CORE ENGINES (OPTIMIZED):**
        - ⚡ BERT/DistilBART (Text)
        - ⚡ Wav2Vec2 Base (Audio)
        - ⚡ Vision Transformer (Vision)
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
        st.markdown("## 📥 INPUT SENSOR ARRAY")
        st.caption("Universal Neural Terminal")
        
        st.markdown("### ENABLE SENSORS")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        if 'sensor_text' not in st.session_state: st.session_state.sensor_text = True
        if 'sensor_voice' not in st.session_state: st.session_state.sensor_voice = False
        if 'sensor_image' not in st.session_state: st.session_state.sensor_image = False
        if 'sensor_video' not in st.session_state: st.session_state.sensor_video = False

        with m_col1:
            st.session_state.sensor_text = st.toggle("📝 TEXT", value=st.session_state.sensor_text)
        with m_col2:
            st.session_state.sensor_voice = st.toggle("🎤 VOICE", value=st.session_state.sensor_voice)
        with m_col3:
            st.session_state.sensor_image = st.toggle("🖼️ IMAGE", value=st.session_state.sensor_image)
        with m_col4:
            st.session_state.sensor_video = st.toggle("📹 LIVE", value=st.session_state.sensor_video)

        
        st.markdown("---")
        
        text_input = ""
        audio_file = None
        image_input = None
        detected_modalities = []

        # Always available based on toggles
        if st.session_state.sensor_text:
            st.markdown("#### ✍️ TEXT CONSOLE")
            text_input = st.text_area(
                "Neural Message",
                placeholder="Type message for analysis...",
                height=100,
                key="p_text_input_v2"
            )
            if text_input: detected_modalities.append("📝 TEXTUAL")

        if st.session_state.sensor_voice:
            st.markdown("#### 🎙️ ACOUSTIC SENSOR")
            try:
                from audio_recorder_streamlit import audio_recorder
                live_audio_bytes = audio_recorder(text="Record Voice", icon_size="2x", key="p_mic_rec_v2")
                if live_audio_bytes:
                    audio_file = io.BytesIO(live_audio_bytes)
                    audio_file.name = "live_audio.wav"
                    detected_modalities.append("🎤 LIVE ACOUSTIC")
                    
                    # PROACTIVE AUDIO ANALYSIS: Store for live synthesis
                    if audio_model is None: audio_model = load_audio_engine()
                    with st.spinner("🎙️ Synchronizing Acoustic Trace..."):
                        a_label, a_conf = audio_model.predict(audio_file)
                        st.session_state.last_audio_emotion = (a_label, a_conf)
                        st.toast(f"Audio Synced: {a_label.upper()}", icon="🎤")
                
                if 'last_audio_emotion' in st.session_state:
                    st.caption(f"Active Audio Trace: **{st.session_state.last_audio_emotion[0].upper()}** ({st.session_state.last_audio_emotion[1]:.1%})")
                    if st.button("🗑️ Clear Audio Trace", key="clear_audio_v2"):
                        del st.session_state.last_audio_emotion
                        st.rerun()
            except Exception as e:
                st.error("Audio hardware unreachable.")


        if st.session_state.sensor_image:
            st.markdown("#### �️ OPTICAL SENSOR")
            uploaded_img = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'], key="p_img_up_v2")
            cam_img = st.camera_input("Take Snapshot", key="p_cam_snap_v2")
            
            if uploaded_img:
                image_input = Image.open(uploaded_img)
                detected_modalities.append("�️ UPLOADED IMAGE")
            elif cam_img:
                image_input = Image.open(cam_img)
                detected_modalities.append("📷 SNAPSHOT")

        if st.session_state.sensor_video:
            st.markdown("#### 📹 REAL-TIME NEURAL SCAN")
            st.info("Continuous intent prediction via direct camera uplink.")
            
            # Use columns for scan controls
            c1, c2 = st.columns(2)
            with c1:
                run_scan = st.toggle("ACTIVATE NEURAL SCANNER", value=False, key="scan_active_toggle_v2")
            with c2:
                f_rate = st.select_slider("Scan Frequency", options=["Low", "Medium", "High"], value="Medium", key="f_rate_v2")
                sleep_time = {"Low": 0.5, "Medium": 0.1, "High": 0.02}[f_rate]
            
            if run_scan:
                import cv2
                # Initialize camera
                cap = cv2.VideoCapture(0)
                
                if not cap.isOpened():
                    st.error("❌ CAMERA NOT FOUND: Please check hardware connection or permissions.")
                else:
                    frame_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    # Pre-load vision engine
                    if vision_model is None:
                        with st.spinner("🔄 Synchronizing Vision Engine..."):
                            vision_model = load_vision_engine()
                    if text_model is None and st.session_state.sensor_text:
                        text_model = load_text_engine()
                    if audio_model is None and st.session_state.sensor_voice:
                        audio_model = load_audio_engine()
                    
                    try:

                        while cap.isOpened() and st.session_state.get("scan_active_toggle_v2", False):
                            ret, frame = cap.read()
                            if not ret: 
                                st.error("Failed to capture stream.")
                                break
                            
                            # Process Vision
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            label, score, annotated_frame = vision_model.predict(frame_rgb)
                            
                            v_emotion = (label, score) if label else None
                            
                            # Integrate Text if available
                            t_probs = None
                            if st.session_state.sensor_text and text_input:
                                t_probs, _, _ = text_model.predict(text_input)
                            
                            # Integrate Last Audio if available
                            a_emotion = st.session_state.get('last_audio_emotion') if st.session_state.sensor_voice else None
                            
                            # FUSE LIVE
                            f_intent, f_conf, f_scores, f_action, f_mod_probs = fuse_multimodal(
                                text_probs=t_probs,
                                vision_emotion=v_emotion,
                                audio_emotion=a_emotion, 
                                weights={'text': w_text, 'audio': w_audio, 'vision': w_vision}
                            )
                            
                            # Update UI
                            audio_indicator = f'<span style="color: #a855f7; font-size: 0.7rem;">+ 🎤 AUDIO ({a_emotion[0].upper()})</span>' if a_emotion else ''
                            
                            status_placeholder.markdown(f"""
                            <div style="background: rgba(99, 102, 241, 0.2); padding: 15px; border-radius: 12px; border: 1px solid var(--primary); animation: pulse-border 2s infinite alternate;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: var(--accent); font-family: 'JetBrains Mono'; font-size: 0.8rem;">[ LIVE NEURAL FEED ]</span>
                                    <span style="color: #10b981; font-size: 0.7rem;">● LIVE SYNTHESIS ACTIVE</span>
                                </div>
                                <div style="margin-top: 10px;">
                                    <span style="color: var(--text-dim); font-size: 0.8rem;">DETECTED INTENT: {audio_indicator}</span><br>
                                    <span style="color: white; font-size: 1.8rem; font-weight: 800; letter-spacing: 0.05em;">{f_intent.upper()}</span>
                                    <span style="float: right; color: var(--accent); font-size: 1.2rem; font-weight: 700; margin-top: 10px;">{f_conf:.1%}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            
                            frame_placeholder.image(annotated_frame, channels="RGB", use_container_width=True)
                            time.sleep(sleep_time)
                            
                    except Exception as loop_err:
                        st.error(f"Scan Loop Error: {loop_err}")
                    finally:
                        cap.release()
                        st.info("Scanner Offline.")

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
        st.caption("Fused Adaptive Processor")
        
        # Predict button with better styling
        predict_btn = st.button("🚀 EXECUTE PREDICTION", type="primary", use_container_width=True)
        
        if predict_btn or (st.session_state.sensor_video and st.session_state.get("scan_active_toggle_v2", False)):
            # If it's a manual button press, we do the full deep analysis
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
                active_signals = []
                
                # 1. Process Text Component
                if st.session_state.sensor_text and text_input:
                    status_text.text("📡 INTERCEPTING TEXT STREAM...")
                    progress_bar.progress(20)
                    try:
                        if text_model is None: text_model = load_text_engine()
                        scores, primary, conf = text_model.predict(text_input)
                        text_probs = scores
                        active_signals.append(f"Text")
                    except Exception as e: st.error(f"Text error: {e}")
                
                # 2. Process Audio Component
                if st.session_state.sensor_voice and audio_file:
                    status_text.text("🎙️ DECODING ACOUSTIC SIGNALS...")
                    progress_bar.progress(50)
                    try:
                        if audio_model is None: audio_model = load_audio_engine()
                        emotion_label, emotion_conf = audio_model.predict(audio_file)
                        if emotion_label:
                            audio_emotion = (emotion_label, emotion_conf)
                            active_signals.append(f"Audio")
                    except Exception as e: st.error(f"Audio error: {e}")
                
                # 3. Process Vision Component
                if st.session_state.sensor_image and image_input:
                    status_text.text("👁️ ANALYZING OPTICAL VECTORS...")
                    progress_bar.progress(75)
                    try:
                        if vision_model is None: vision_model = load_vision_engine()
                        emotion_label, emotion_conf, annotated_img = vision_model.predict(image_input)
                        if emotion_label:
                            vision_emotion = (emotion_label, emotion_conf)
                            active_signals.append(f"Vision")
                            if use_debug: st.image(annotated_img, caption="Vector Overlay", use_container_width=True)
                    except Exception as e: st.error(f"Vision error: {e}")
                
                # Fusion
                status_text.text("🔄 Fusing multimodal data...")
                progress_bar.progress(90)
                
                try:
                    # Create weights dictionary
                    fusion_weights = {'text': w_text, 'audio': w_audio, 'vision': w_vision}
                    
                    final_intent, final_conf, all_scores, action, modality_probs = fuse_multimodal(
                        text_probs=text_probs,
                        audio_emotion=audio_emotion,
                        vision_emotion=vision_emotion,
                        weights=fusion_weights
                    )
                    
                    # Add to history
                    add_to_history(text_input, "Audio" if audio_file else None, "Image" if image_input else None, final_intent, final_conf, action)
                
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    time.sleep(0.5)
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display stunning results
                    st.markdown("---")
                    badge_class = f"badge-{final_intent.lower()}"
                    insight = generate_ai_insight(final_intent, final_conf, modality_probs, text_input, audio_emotion, vision_emotion)
                    
                    res_col1, res_col2 = st.columns([1.2, 0.8])
                    with res_col1:
                        st.markdown(f"""
    <div class="result-box">
    <div class="intent-label">System Analysis Result</div>
    <h2 class="intent-value">{final_intent}</h2>
    <div class="intent-badge {badge_class}">Confidence: {final_conf:.1%}</div>
    <div class="action-card" style="margin-top: 20px; text-align: left; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; border-left: 4px solid var(--accent);">
    <div style="font-size: 0.7rem; color: var(--accent); font-family: 'JetBrains Mono'; text-transform: uppercase;">Neural Trace Insight</div>
    <div style="font-size: 0.95rem; margin-top: 5px; color: #f8fafc; font-style: italic;">"{insight}"</div>
    </div>
    </div>
    """, unsafe_allow_html=True)
                    
                    with res_col2:
                        st.plotly_chart(create_confidence_gauge(final_conf, final_intent), use_container_width=True)
                    
                    # Modality Comparison
                    st.plotly_chart(create_modality_comparison_chart(modality_probs, all_scores), use_container_width=True)
                    
                    # Quick Actions
                    st.markdown("### ⚡ QUICK ACTIONS")
                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        if st.button("📝 Draft Reply", use_container_width=True, key="btn_reply"): st.toast("Drafting response...")
                    with act_col2:
                        if st.button("🚨 Transfer", use_container_width=True, key="btn_trans"): st.toast("Transferring...")

                except Exception as e:
                    st.error(f"❌ FUSION COLLAPSE: {e}")
        
        else:
            # Placeholder when no analysis is active
            st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; border: 2px dashed rgba(255,255,255,0.05); border-radius: 24px; color: var(--text-dim);">
                <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">🧠</div>
                <h3>NEURAL CORE STANDBY</h3>
                <p>Activate sensors and execute prediction to begin analysis cycle.</p>
            </div>
            """, unsafe_allow_html=True)

        
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
