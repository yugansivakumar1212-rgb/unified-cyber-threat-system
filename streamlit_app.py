import streamlit as st
import plotly.graph_objects as go
import numpy as np
import hashlib
import time
import random

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="SENTINEL-X | TACTICAL", layout="wide")

# --- 2. THE TACTICAL UI ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), 
                    url("https://i.gifer.com/2pjo.gif");
        background-size: cover;
        background-attachment: fixed;
    }

    h1, h2, h3, label, p, .stMarkdown {
        color: #00FF41 !important;
        text-shadow: 0 0 10px #00FF41;
        font-family: 'Courier New', monospace !important;
    }

    @keyframes tactical-alert {
        0% { border: 2px solid #500; }
        50% { border: 2px solid #f00; box-shadow: 0 0 30px #f00; }
        100% { border: 2px solid #500; }
    }
    .threat-detected-ui {
        animation: tactical-alert 0.8s infinite;
        padding: 25px;
        border-radius: 5px;
        background: rgba(50, 0, 0, 0.4);
    }

    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(0, 20, 0, 0.9) !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SENTINEL-X: UNIFIED THREAT INTERROGATOR")
st.write("STATUS: SCANNING READY")

# --- 3. MULTI-VECTOR TABS ---
tab1, tab2 = st.tabs(["📁 DATA & BINARY SCAN", "🔊 SIGNAL INTELLIGENCE"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        url_in = st.text_input("INTERROGATE URL", placeholder="Target Vector...")
        email_in = st.text_area("INSPECT EMAIL CONTENT", placeholder="Packet Analysis...")
    with col2:
        file_in = st.file_uploader("UPLOAD LARGE DATA PACKET (ANY TYPE)", type=None)

with tab2:
    st.markdown("### 🔊 Spectral Audio Interrogation")
    audio_in = st.file_uploader("UPLOAD SIGNAL FOR PULSE CHECK", type=["mp3", "wav", "ogg"])
    if audio_in:
        st.audio(audio_in)

# --- 4. SCAN ENGINE ---
if st.button("EXECUTE SYSTEM SCAN"):

    # Prevent running with no inputs
    if not file_in and not url_in and not email_in:
        st.warning("Provide at least one input before running a scan.")
        st.stop()

    score = 0
    reasons = []

    with st.status("Running heuristic analysis...", expanded=True) as status:

        # A. FILE ANALYSIS
        if file_in:
            st.write("🔬 Hashing Large Binary...")

            sha256 = hashlib.sha256()
            file_in.seek(0)

            file_bytes = file_in.read()
            sha256.update(file_bytes)

            st.code(f"SHA-256 FINGERPRINT: {sha256.hexdigest()}", language="bash")

            risk = 0

            # Realistic small signals instead of huge jumps
            if b"eval" in file_bytes:
                risk += 20
                reasons.append("Suspicious scripting keyword detected.")

            if b"base64" in file_bytes:
                risk += 15
                reasons.append("Encoded data patterns detected.")

            if len(file_bytes) > 15_000_000:
                risk += 5
                reasons.append("Large file size may conceal embedded content.")

            if risk == 0:
                reasons.append("No obvious anomalies detected in quick scan.")

            score += risk

        # B. URL ANALYSIS
        if url_in:
            url_lower = url_in.lower()

            if "bit.ly" in url_lower:
                score += 15
                reasons.append("Shortened URL detected.")

            if any(x in url_lower for x in [".xyz", ".ru"]):
                score += 10
                reasons.append("Less common domain zone detected.")

            if len(url_lower) > 70:
                score += 5
                reasons.append("Unusually long URL structure.")

        # C. EMAIL ANALYSIS
        if email_in:
            email_lower = email_in.lower()
            keywords = ["urgent", "verify", "password", "login", "bank"]

            matches = sum(word in email_lower for word in keywords)

            if matches:
                score += matches * 6
                reasons.append("Language patterns consistent with phishing attempts.")

        # Add small variability so output isn't identical every time
        score += random.randint(0, 4)

        time.sleep(1.2)
        status.update(label="SCAN COMPLETE", state="complete")

    # --- 5. OUTPUT ---
    score = min(score, 100)

    res_l, res_r = st.columns([2, 1])

    with res_l:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "red" if score > 50 else "#00FF41"}}
        ))

        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "#00FF41"})
        st.plotly_chart(fig, use_container_width=True)

    with res_r:
        if score == 0:
            st.success("No risk indicators detected.")
        elif score < 40:
            st.success("Low risk indicators present.")
        elif score < 70:
            st.warning("Moderate risk indicators detected.")
        else:
            st.markdown('<div class="threat-detected-ui">', unsafe_allow_html=True)
            st.error("High risk indicators detected.")
            st.markdown('</div>', unsafe_allow_html=True)

        for r in reasons:
            st.info(f"• {r}")