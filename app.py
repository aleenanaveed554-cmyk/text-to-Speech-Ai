import asyncio
import os
import tempfile

import edge_tts
import streamlit as st

st.set_page_config(
    page_title="Voxify AI | Text to Speech",
    page_icon="🎙️",
    layout="wide"
)

# Custom Design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

.stApp {
    background: radial-gradient(circle at 15% 5%, #24305b 0, transparent 32%),
                radial-gradient(circle at 90% 15%, #183d49 0, transparent 28%),
                #0b1020;
    color: #f5f7ff;
    font-family: 'DM Sans', sans-serif;
}
.block-container {
    max-width: 1120px;
    padding-top: 2.2rem;
}
.hero {
    padding: 28px 30px;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 24px;
    background: linear-gradient(120deg, rgba(91,86,214,.22), rgba(27,177,177,.12));
    margin-bottom: 24px;
}
.eyebrow {
    color: #8ee9df;
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: 2px;
}
.hero h1 {
    font-size: clamp(2rem, 5vw, 3.35rem);
    color: white;
}
.hero p {
    color: #bdc7dc;
}
.panel {
    background: rgba(20, 28, 49, .88);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 20px;
    padding: 22px;
}
div[data-testid="stTextArea"] textarea {
    background: #101a30 !important;
    color: white !important;
    border: 1px solid #344260 !important;
    border-radius: 14px !important;
}
.stButton > button, .stDownloadButton > button {
    border: 0;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 700;
    background: linear-gradient(90deg,#7568f5,#27bdb4);
    color: white;
    width: 100%;
}
.info-card {
    background: #111c32;
    border: 1px solid #293958;
    border-radius: 14px;
    padding: 14px 16px;
    color: #c8d4e9;
}
.footer {
    text-align: center;
    color: #8290aa;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="hero">
    <div class="eyebrow">✦ AI VOICE STUDIO</div>
    <h1>Turn your words into voice.</h1>
    <p>Create clear, natural-sounding speech in seconds.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.55, 1], gap="large")

# Text Input
with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### ✍️ Your Script")

    text = st.text_area(
        "Enter your text",
        height=250,
        placeholder="Type or paste your text here...",
        label_visibility="collapsed",
        max_chars=5000
    )

    st.caption(f"{len(text)} / 5000 characters")
    st.markdown('</div>', unsafe_allow_html=True)

# Voice Settings
with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Voice Settings")

    gender = st.selectbox(
        "Voice Style",
        ["Female", "Male"]
    )

    if gender == "Female":
        voices = {
            "Jenny - US English": "en-US-JennyNeural",
            "Aria - US English": "en-US-AriaNeural",
            "Sonia - UK English": "en-GB-SoniaNeural",
            "Uzma - Urdu": "ur-PK-UzmaNeural"
        }
    else:
        voices = {
            "Guy - US English": "en-US-GuyNeural",
            "Christopher - US English": "en-US-ChristopherNeural",
            "Ryan - UK English": "en-GB-RyanNeural",
            "Asad - Urdu": "ur-PK-AsadNeural"
        }

    voice_name = st.selectbox(
        "Choose Voice",
        list(voices.keys())
    )

    speed = st.slider(
        "Speech Speed",
        min_value=0.75,
        max_value=1.25,
        value=1.0,
        step=0.05
    )

    st.caption("0.75x Slower | 1.0x Normal | 1.25x Faster")

    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="info-card">
        <b>🎧 Studio Quality Audio</b>
        <p>Generate, listen and download your MP3 audio.</p>
    </div>
    """, unsafe_allow_html=True)

# Audio Generation
st.write("")

col1, col2 = st.columns([3, 1])

with col1:
    generate = st.button(
        "✨ Generate Speech",
        use_container_width=True
    )

with col2:
    clear = st.button(
        "↻ Clear Text",
        use_container_width=True
    )

if clear:
    st.session_state["generated_audio"] = None
    st.rerun()


async def generate_audio(content, voice, rate, output_path):
    communicate = edge_tts.Communicate(
        content,
        voice,
        rate=rate
    )
    await communicate.save(output_path)


if generate:

    if not text.strip():
        st.warning("Please enter some text first.")

    else:

        rate_percent = int((speed - 1) * 100)
        rate = f"{rate_percent:+d}%"

        with st.spinner("Generating your AI voice..."):

            try:
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp3"
                ) as temp_file:

                    temp_path = temp_file.name

                asyncio.run(
                    generate_audio(
                        text.strip(),
                        voices[voice_name],
                        rate,
                        temp_path
                    )
                )

                with open(temp_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()

                st.session_state["generated_audio"] = audio_bytes
                st.session_state["generated_voice"] = voice_name

                st.success("Your speech is ready!")

            except Exception as error:
                st.error(
                    "Audio generation failed. "
                    "Please check your internet connection."
                )
                st.caption(str(error))

            finally:
                if "temp_path" in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)


# Audio Player
if st.session_state.get("generated_audio"):

    st.write("")

    st.markdown('<div class="panel">', unsafe_allow_html=True)

    st.markdown("### 🎵 Your Generated Audio")

    st.caption(
        f"Voice: {st.session_state.get('generated_voice', '')}"
    )

    audio_bytes = st.session_state["generated_audio"]

    st.audio(
        audio_bytes,
        format="audio/mp3"
    )

    st.download_button(
        "⬇️ Download MP3",
        data=audio_bytes,
        file_name="voxify_ai_speech.mp3",
        mime="audio/mpeg",
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


# Footer
st.markdown("""
<div class="footer">
    VOXIFY AI | Your Words, Beautifully Spoken
</div>
""", unsafe_allow_html=True)
