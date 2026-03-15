/**
 * AETHER E-COMMERCE ENGINE
 * 2-Tier Support: AI first, then Senior Specialist if needed
 */

const API_BASE = "http://localhost:8000";

// ─── Conversation State ───────────────────────────────────────────────────────
let conversationState = "idle"; // "idle" | "ai_replied" | "escalated" | "resolved"
let currentCaseId = null;
let conversationLog = []; // Full log: [{role, text}]
let repliesSeenCount = 0;
let seniorPollTimer = null;

// ─── Shopping State ───────────────────────────────────────────────────────────
let cart = [];
let userProfile = null;

// ─── Media State ──────────────────────────────────────────────────────────────
let isCameraActive = false;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let stream = null;
let msgCounter = 0;

// ─── DOM ──────────────────────────────────────────────────────────────────────
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

// ─── AI Response Templates ─────────────────────────────────────────────────────
const AI_TEMPLATES = {
    Inquiry: [
        "Great question! Our AetherBook Ultra 14 features Neural Chip M1 with 32GB RAM — perfect for professionals. Would you like more details or a comparison with the AetherBook Air?",
        "Happy to help! For audio, our Studio Pro ANC headphones offer 40-hour battery and spatial audio. The Aether Buds are great for everyday neural noise cancellation. Which one interests you?",
        "I can help with that! To check your order status, you can visit the Orders section in the top bar after signing in. Need help with anything else?"
    ],
    Complaint: [
        "I'm really sorry to hear that — you deserve a better experience. Let me look into this right now. Could you share your order number so I can pull up the details and find the quickest resolution?",
        "That's not the experience we want you to have, and I sincerely apologize. I'm checking our records for your case. In the meantime, would a replacement or a full refund work better for you?",
        "I completely understand your frustration, and I take this seriously. I've already flagged this internally. Can you confirm the product name and date of purchase so I can resolve this faster?"
    ],
    Escalation: [
        "I hear you, and I want to assure you this is being treated as a high-priority case. I've documented everything you've shared. Would you prefer I connect you with a senior specialist who can take direct action?",
        "I understand this situation requires immediate attention. I've escalated your case internally. A senior human specialist is reviewing this. They'll respond to you shortly — please stay on the chat.",
        "You're absolutely right to push for a better resolution. I've marked this as urgent. If my answer doesn't fully address your concern, please let me know and I'll connect you directly to a senior team member."
    ],
    Distress: [
        "I can see you're in a very stressful situation and I want to help immediately. I'm escalating this directly to a senior human specialist right now. Please stay calm — you'll hear from them within moments.",
        "Your situation has my full attention. I'm treating this as an emergency and escalating immediately. A human specialist will be with you shortly. Please don't worry — we'll sort this out together.",
        "I've detected this is urgent. I'm connecting you with a senior team member right now. You don't have to handle this alone — help is on the way."
    ],
    Neutral: [
        "Thanks for reaching out! I'm here to help with any questions about our product lineup, orders, or technical support. What can I assist you with today?",
        "Of course! Whether it's about the Aether Vision series, your order, or a return, I'm happy to guide you. What's on your mind?",
        "Hello! Great to have you here. Tell me what you need and I'll do my best to sort it out for you right away."
    ]
};

function getAIReply(intent) {
    const list = AI_TEMPLATES[intent] || AI_TEMPLATES.Neutral;
    return list[Math.floor(Math.random() * list.length)];
}

// ─── Chat helpers ──────────────────────────────────────────────────────────────
function appendChat(role, msg, id) {
    const div = document.createElement('div');
    const msgId = id || `msg-${msgCounter++}`;
    div.id = msgId;
    div.className = `chat-msg ${role}`;
    div.innerText = msg;
    chatHistory.appendChild(div);
    chatHistory.scrollTo({ top: chatHistory.scrollHeight, behavior: 'smooth' });
    return msgId;
}

function updateChat(id, msg) {
    const div = document.getElementById(id);
    if (div) div.innerText = msg;
}

function showSatisfactionButtons() {
    // Remove any existing satisfaction bar
    const existing = document.getElementById('satisfaction-bar');
    if (existing) existing.remove();

    const bar = document.createElement('div');
    bar.id = 'satisfaction-bar';
    bar.style = `
        display: flex; gap: 8px; padding: 10px 0;
        animation: fadeIn 0.4s ease;
    `;
    bar.innerHTML = `
        <button onclick="markResolved()" style="
            flex:1; padding:8px; border:none; border-radius:8px;
            background:#d1fae5; color:#065f46; font-weight:700;
            cursor:pointer; font-size:0.8rem;
        ">✅ That helped!</button>
        <button onclick="escalateToSenior()" style="
            flex:1; padding:8px; border:none; border-radius:8px;
            background:#fee2e2; color:#b91c1c; font-weight:700;
            cursor:pointer; font-size:0.8rem;
        ">❌ Not satisfied — connect me to a human</button>
    `;
    chatHistory.appendChild(bar);
    chatHistory.scrollTo({ top: chatHistory.scrollHeight, behavior: 'smooth' });
}

function removeSatisfactionButtons() {
    const bar = document.getElementById('satisfaction-bar');
    if (bar) bar.remove();
}

function markResolved() {
    removeSatisfactionButtons();
    conversationState = "resolved";
    currentCaseId = null;
    appendChat("ai", "Glad I could help! 😊 Feel free to reach out anytime. Happy shopping!");
}

async function escalateToSenior() {
    removeSatisfactionButtons();
    if (!currentCaseId) return;

    conversationState = "escalated";

    // Disable input so user knows they're waiting
    sendBtn.disabled = true;
    textInput.placeholder = "Waiting for a Senior Specialist...";
    textInput.disabled = true;

    appendChat("system-notice", "🔔 Connecting you to a Senior Specialist. Please hold — they'll respond shortly.");

    // Notify backend to mark as escalated by the user
    try {
        await fetch(`${API_BASE}/escalate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ case_id: currentCaseId, conversation: conversationLog })
        });
    } catch (e) { console.warn("Escalation notify failed:", e); }

    // Start polling for senior reply
    startSeniorPolling();
}

function startSeniorPolling() {
    if (seniorPollTimer) clearInterval(seniorPollTimer);
    repliesSeenCount = 0;

    seniorPollTimer = setInterval(async () => {
        if (!currentCaseId || conversationState !== "escalated") {
            clearInterval(seniorPollTimer);
            return;
        }

        try {
            const resp = await fetch(`${API_BASE}/case/${currentCaseId}/replies`);
            if (!resp.ok) return;
            const data = await resp.json();

            if (data.replies.length > repliesSeenCount) {
                // Re-enable input
                sendBtn.disabled = false;
                textInput.disabled = false;
                textInput.placeholder = "Continue the conversation...";

                for (let i = repliesSeenCount; i < data.replies.length; i++) {
                    const reply = data.replies[i];
                    appendChat("senior", `👤 Senior Specialist: ${reply.text}`);
                    conversationLog.push({ role: "senior", text: reply.text });
                }
                repliesSeenCount = data.replies.length;
                conversationState = "resolved";
            }
        } catch (e) {
            // silent
        }
    }, 3000);
}

// ─── Main send logic ──────────────────────────────────────────────────────────
sendBtn.onclick = async () => {
    const text = textInput.value.trim();
    if (!text && !window.lastAudioBlob && !isCameraActive && !window.lastImageBlob) return;
    if (conversationState === "escalated") return; // Locked while waiting

    removeSatisfactionButtons();
    sendBtn.disabled = true;
    sendBtn.innerText = "⏳";

    const userText = text || "(multimodal input)";
    appendChat("user", userText);
    conversationLog.push({ role: "user", text: userText });
    textInput.value = "";

    const aiMsgId = appendChat("ai-loading", "Analyzing your message...");

    try {
        const formData = new FormData();
        if (text) formData.append("text", text);

        if (window.lastAudioBlob) {
            formData.append("audio", window.lastAudioBlob, "audio.wav");
            window.lastAudioBlob = null;
        }
        if (window.lastImageBlob) {
            formData.append("image", window.lastImageBlob, "upload.jpg");
            window.lastImageBlob = null;
            imgBtn.classList.remove('active');
            imgBtn.innerText = "🖼️ Image";
        }
        if (isCameraActive) {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            const blob = await new Promise(res => canvas.toBlob(res, 'image/jpeg', 0.8));
            formData.append("image", blob, "face.jpg");
        }

        const response = await fetch(`${API_BASE}/predict`, { method: 'POST', body: formData });
        const data = await response.json();

        currentCaseId = data.id;
        conversationState = "ai_replied";

        // Update analytics panel
        updateAnalytics(data);

        // ── Step 1: Replace loading bubble with INTENT RESULT badge ──
        const intentColors = {
            Inquiry: { bg: "#dbeafe", color: "#1d4ed8", icon: "🔍" },
            Complaint: { bg: "#fee2e2", color: "#b91c1c", icon: "⚠️" },
            Escalation: { bg: "#fef3c7", color: "#92400e", icon: "🚨" },
            Distress: { bg: "#ede9fe", color: "#6d28d9", icon: "🆘" },
            Neutral: { bg: "#d1fae5", color: "#065f46", icon: "💬" }
        };
        const ic = intentColors[data.intent] || intentColors.Neutral;
        const confidencePct = (data.confidence * 100).toFixed(1);

        const aiDiv = document.getElementById(aiMsgId);
        if (aiDiv) {
            aiDiv.className = "chat-msg intent-result";
            aiDiv.innerHTML = `
                <div style="
                    background:${ic.bg}; color:${ic.color};
                    border-radius:12px; padding:12px 16px;
                    font-size:0.85rem; line-height:1.6;
                    border-left: 4px solid ${ic.color};
                ">
                    <div style="font-weight:800; font-size:1rem; margin-bottom:6px;">
                        ${ic.icon} Detected Intent: <span style="text-transform:uppercase;">${data.intent}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                        <span style="font-weight:600;">Confidence:</span>
                        <div style="flex:1; background:rgba(0,0,0,0.1); border-radius:20px; height:8px;">
                            <div style="width:${confidencePct}%; background:${ic.color}; height:8px; border-radius:20px;"></div>
                        </div>
                        <span style="font-weight:700;">${confidencePct}%</span>
                    </div>
                    <div style="font-size:0.78rem; opacity:0.85;">🎯 Action: ${data.action}</div>
                </div>
            `;
        }

        // ── Step 2: Now show the AI reply below ──
        const aiReply = getAIReply(data.intent);
        conversationLog.push({ role: "ai", text: aiReply });
        appendChat("ai", aiReply);

        // If Distress or Escalation, auto-escalate without asking
        if (data.intent === "Distress" || data.intent === "Escalation") {
            setTimeout(() => {
                if (conversationState === "ai_replied") {
                    escalateToSenior();
                }
            }, 2500);
        } else {
            // Show satisfaction buttons for other intents
            showSatisfactionButtons();
        }

    } catch (err) {
        const aiDiv = document.getElementById(aiMsgId);
        if (aiDiv) {
            aiDiv.className = "chat-msg ai";
            aiDiv.innerText = "⚠️ Connection error. Please ensure server.py is running on port 8000.";
        }
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerText = "Send";
    }
};

// Allow Enter key to send
textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

// ─── Analytics ────────────────────────────────────────────────────────────────
function updateAnalytics(data) {
    analytics.classList.remove('hidden');
    document.getElementById('detected-intent').innerText = data.intent;
    const perc = (data.confidence * 100).toFixed(1) + "%";
    confBar.style.width = perc;
    confBar.title = `${data.intent} — ${perc} confidence`;
}

// ─── Cart ─────────────────────────────────────────────────────────────────────
function addToCart(name, price) {
    cart.push({ name, price });
    updateCartUI();
    const toast = document.createElement('div');
    toast.style = "position:fixed;bottom:20px;left:20px;background:#2563eb;color:white;padding:12px 24px;border-radius:12px;font-weight:800;z-index:9999;";
    toast.innerText = `✅ ${name} added to Bag!`;
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
            <button onclick="removeFromCart(${idx})" style="background:none;border:none;color:#ff4444;cursor:pointer;font-size:1.1rem;">✕</button>
        `;
        cartItemsContainer.appendChild(div);
    });
    cartTotalLabel.innerText = `₹${total.toLocaleString()}`;
}

window.removeFromCart = (idx) => { cart.splice(idx, 1); updateCartUI(); };

const buyNowBtn = document.querySelector('.buy-now-btn');
if (buyNowBtn) {
    buyNowBtn.onclick = () => {
        if (cart.length === 0) return alert("Your bag is empty!");
        alert("🎉 Order placed! Thank you for shopping with Aether.");
        cart = [];
        updateCartUI();
        cartModal.classList.add('hidden');
    };
}

// ─── Sign In ──────────────────────────────────────────────────────────────────
signinNavBtn.onclick = () => signinModal.classList.remove('hidden');
closeSignin.onclick = () => signinModal.classList.add('hidden');
doSigninBtn.onclick = () => {
    const email = document.getElementById('user-email').value;
    if (!email) return;
    userProfile = { email };
    signinNavBtn.innerText = `Hi, ${email.split('@')[0]} 👋`;
    signinModal.classList.add('hidden');
    appendChat("ai", `Welcome back, ${email.split('@')[0]}! Prices are showing in INR for your region. How can I help you today?`);
};

// ─── Cart sidebar ─────────────────────────────────────────────────────────────
cartBtn.onclick = () => cartModal.classList.remove('hidden');
closeCart.onclick = () => cartModal.classList.add('hidden');

function scrollToId(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}

// ─── Support Chat FAB ─────────────────────────────────────────────────────────
supportBtn.onclick = () => {
    modal.classList.remove('hidden');
    supportBtn.classList.add('hidden');
};
closeBtn.onclick = () => {
    modal.classList.add('hidden');
    supportBtn.classList.remove('hidden');
    stopCamera();
    clearInterval(seniorPollTimer);
};

// ─── Camera ───────────────────────────────────────────────────────────────────
camBtn.onclick = async () => {
    if (!isCameraActive) {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 }, audio: false });
            video.srcObject = stream;
            videoContainer.classList.remove('hidden');
            camBtn.classList.add('active');
            camBtn.innerText = "📷 Stop";
            isCameraActive = true;
            appendChat("ai", "Live Vision is active — I'll analyze your facial expression when you send a message.");
        } catch (err) {
            alert("Camera access denied. Please allow camera permissions.");
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
        stream = null;
    }
}

// ─── Image Upload ─────────────────────────────────────────────────────────────
imgBtn.onclick = () => imgInput.click();
imgInput.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
        window.lastImageBlob = file;
        imgBtn.classList.add('active');
        imgBtn.innerText = "🖼️ Ready";
        appendChat("ai", "Image received — I'll include it in the next analysis.");
    }
};

// ─── Microphone ───────────────────────────────────────────────────────────────
micBtn.onclick = async () => {
    if (!isRecording) {
        try {
            const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(micStream);
            audioChunks = [];
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = () => {
                window.lastAudioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                appendChat("ai", "Voice sample captured and ready to analyze.");
            };
            mediaRecorder.start();
            micBtn.classList.add('active');
            micBtn.innerText = "🛑 Stop";
            isRecording = true;
        } catch (err) {
            alert("Microphone access denied.");
        }
    } else {
        mediaRecorder.stop();
        micBtn.classList.remove('active');
        micBtn.innerText = "🎤 Voice";
        isRecording = false;
    }
};
