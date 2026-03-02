/**
 * AETHER E-COMMERCE ENGINE
 * Real-world integration for Neural Intent Core
 */

const API_URL = "http://localhost:8000/predict";

// State Management
let isCameraActive = false;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let stream = null;
let msgCounter = 0;
let cart = []; // Real cart storage
let userProfile = null; // User sign-in state


// DOM Elements
const supportBtn = document.getElementById('neural-support-btn');
const modal = document.getElementById('support-modal');
const closeBtn = document.getElementById('close-support');
const camBtn = document.getElementById('cam-btn');
const micBtn = document.getElementById('mic-btn');
const imgBtn = document.getElementById('img-btn');
const imgInput = document.getElementById('image-upload');
const video = document.getElementById('support-cam');

const videoContainer = document.getElementById('sensor-preview');
const sendBtn = document.getElementById('send-btn');
const textInput = document.getElementById('support-text');
const chatHistory = document.getElementById('chat-history');
const analytics = document.getElementById('neural-analytics');
const confBar = document.getElementById('intent-conf-bar');

// DOM Elements for New Features
const signinNavBtn = document.getElementById('signin-nav-btn');
const signinModal = document.getElementById('signin-modal');
const closeSignin = document.getElementById('close-signin');
const doSigninBtn = document.getElementById('do-signin');
const cartBtn = document.getElementById('cart-btn');
const cartModal = document.getElementById('cart-modal');
const closeCart = document.getElementById('close-cart');
const cartItemsContainer = document.getElementById('cart-items');
const cartTotalLabel = document.getElementById('cart-total-price');
const cartCountLabel = document.getElementById('cart-count');

/** --- Real E-commerce Functions --- **/

// Cart Logic
function addToCart(name, price) {
    cart.push({ name, price });
    updateCartUI();

    // Toast notification
    const toast = document.createElement('div');
    toast.className = "cart-toast";
    toast.style = "position:fixed; bottom:20px; left:20px; background:#2563eb; color:white; padding:12px 24px; border-radius:12px; font-weight:800; z-index:9999;";
    toast.innerText = `Added ${name} to Bag! 👜`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2500);
}

function updateCartUI() {
    cartCountLabel.innerText = cart.length;
    document.getElementById('bag-total-count').innerText = `${cart.length} items`;

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<div class="empty-cart-msg">Your bag is empty. Explore the Aether ecosystem.</div>';
        cartTotalLabel.innerText = '₹0';
        return;
    }

    cartItemsContainer.innerHTML = '';
    let total = 0;
    cart.forEach((item, idx) => {
        total += item.price;
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">₹${item.price.toLocaleString()}</div>
            </div>
            <button onclick="removeFromCart(${idx})" style="background:none; border:none; color:#ff4444; cursor:pointer;">✕</button>
        `;
        cartItemsContainer.appendChild(div);
    });
    cartTotalLabel.innerText = `₹${total.toLocaleString()}`;
}

window.removeFromCart = (idx) => {
    cart.splice(idx, 1);
    updateCartUI();
};

// Sign-In Flow
signinNavBtn.onclick = () => signinModal.classList.remove('hidden');
closeSignin.onclick = () => signinModal.classList.add('hidden');
doSigninBtn.onclick = () => {
    const email = document.getElementById('user-email').value;
    if (!email) return;

    userProfile = { email };
    signinNavBtn.innerText = `Hi, ${email.split('@')[0]}`;
    signinModal.classList.add('hidden');

    // Simulate detecting location and converting to INR
    appendChat("ai", "Location synchronized: India. Prices are now optimized for INR.");
};

// Open/Close Cart
cartBtn.onclick = () => cartModal.classList.remove('hidden');
closeCart.onclick = () => cartModal.classList.add('hidden');

function scrollToId(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}

/** --- Support Interaction --- **/
supportBtn.onclick = () => {
    modal.classList.remove('hidden');
    supportBtn.classList.add('hidden');
};

closeBtn.onclick = () => {
    modal.classList.add('hidden');
    supportBtn.classList.remove('hidden');
    stopCamera();
};

// Fixed Camera Control (Full Aspect Ratio)
camBtn.onclick = async () => {
    if (!isCameraActive) {
        try {
            // Request high-quality stream
            stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 1280, height: 720 },
                audio: false
            });
            video.srcObject = stream;
            videoContainer.classList.remove('hidden');
            camBtn.classList.add('active');
            camBtn.innerText = "📷 Stop Video";
            isCameraActive = true;
            appendChat("ai", "Aether Vision active. I am now analyzing your facial intent.");
        } catch (err) {
            console.error("Camera fail", err);
            alert("Please allow camera access for Aether Vision.");
        }
    } else {
        stopCamera();
    }
};

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        videoContainer.classList.add('hidden');
        camBtn.classList.remove('active');
        camBtn.innerText = "📷 Video";
        isCameraActive = false;
    }
}

// Image Upload Handler
imgBtn.onclick = () => imgInput.click();

imgInput.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
        window.lastImageBlob = file;
        imgBtn.classList.add('active');
        imgBtn.innerText = "🖼️ Uploaded";
        appendChat("ai", "Image trace registered. I am now synthesizing your visual intent.");
    }
};

// Audio Recording
micBtn.onclick = async () => {
    if (!isRecording) {
        try {
            const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(micStream);
            audioChunks = [];

            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                window.lastAudioBlob = audioBlob;
                appendChat("ai", "Voice sample captured. Synthesis ready.");
            };

            mediaRecorder.start();
            micBtn.classList.add('active');
            micBtn.innerText = "🛑 Stop Rec";
            isRecording = true;
        } catch (err) {
            console.error("Mic fail", err);
        }
    } else {
        mediaRecorder.stop();
        micBtn.classList.remove('active');
        micBtn.innerText = "🎤 Voice";
        isRecording = false;
    }
};

// Synthesis Engine
sendBtn.onclick = async () => {
    const text = textInput.value.trim();
    if (!text && !window.lastAudioBlob && !isCameraActive && !window.lastImageBlob) return;

    sendBtn.disabled = true;
    sendBtn.innerText = "⏳";

    appendChat("user", text || "Synthesizing Multimodal Trace...");
    textInput.value = "";

    const aiMsgId = appendChat("ai", "Transmitting neural trace to Aether Core...");

    try {
        const formData = new FormData();
        if (text) formData.append("text", text);

        // Handle Audio
        if (window.lastAudioBlob) {
            formData.append("audio", window.lastAudioBlob, "audio.wav");
            window.lastAudioBlob = null;
        }

        // Handle Static Image Upload
        if (window.lastImageBlob) {
            formData.append("image", window.lastImageBlob, "upload.jpg");
            window.lastImageBlob = null;
            imgBtn.classList.remove('active');
            imgBtn.innerText = "🖼️ Image";
        }

        // Handle Live Video Frame capture (Override static image if both exist)
        if (isCameraActive) {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            const blob = await new Promise(res => canvas.toBlob(res, 'image/jpeg', 0.8));
            formData.append("image", blob, "face.jpg");
        }

        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        updateAnalytics(data);
        updateChat(aiMsgId, synthesizeResponse(data.intent, data.confidence, data.action));

    } catch (err) {
        console.error("Link Failure", err);
        updateChat(aiMsgId, "⚠️ Connection Failure. Make sure server.py is running.");
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerText = "Send";
    }
};

function appendChat(role, msg) {
    const div = document.createElement('div');
    const id = `msg-${msgCounter++}`;
    div.id = id;
    div.className = `chat-msg ${role}`;
    div.innerText = msg;
    chatHistory.appendChild(div);
    chatHistory.scrollTo({ top: chatHistory.scrollHeight, behavior: 'smooth' });
    return id;
}

function updateChat(id, msg) {
    const div = document.getElementById(id);
    if (div) div.innerText = msg;
}

function updateAnalytics(data) {
    analytics.classList.remove('hidden');
    document.getElementById('detected-intent').innerText = data.intent;
    const perc = (data.confidence * 100).toFixed(1) + "%";
    confBar.style.width = perc;
}

function synthesizeResponse(intent, conf, action) {
    const db = {
        "Inquiry": "Based on your inquiry, Aether Vision suggests viewing the Studio series. " + action,
        "Complaint": "I detect dissatisfaction. I have prioritized this for immediate resolution. " + action,
        "Escalation": "High-priority Intent detected. Connecting you to a live specialist. " + action,
        "Distress": "URGENT STATUS. An emergency responder is being notified. " + action,
        "Neutral": "Synthesis complete. How else can I help with your shopping?"
    };
    return db[intent] || "Aether Neural Core: Synthesis Complete.";
}
