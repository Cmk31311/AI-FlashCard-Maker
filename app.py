import os
import json
from typing import List, Dict

import streamlit as st

from utils import (
    extract_text_from_files,
    generate_flashcards_offline,
    generate_flashcards_gemini,  # Gemini generator
    build_mc_options,
)

st.set_page_config(page_title="AI Flashcard Maker", layout="wide")

if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# === Live animated background + glass button bar ===
ANIMATED_BG = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

:root{
  --base:#0b1020; --text:#e6e8f2;
  --card:rgba(255,255,255,0.06); --card-border:rgba(255,255,255,0.08);
}

.stApp{
  background: var(--base);
  color: var(--text);
  font-family:'Inter',system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
}

/* Animated layers holder */
.animated-bg{
  position:fixed; inset:-20%;
  z-index:0; pointer-events:none;
}

/* 1) Slow color gradient */
.animated-bg .bg-gradient{
  position:absolute; inset:0;
  background: linear-gradient(270deg, #0ea5e9, #7c3aed, #22d3ee, #0ea5e9);
  background-size: 600% 600%;
  animation: gradientShift 28s ease-in-out infinite;
  opacity: 0.18; filter: saturate(120%);
}

/* 2) Floating glow blobs */
.animated-bg .bg-blobs{
  position:absolute; inset:0;
  background:
    radial-gradient(40% 40% at 12% 22%, rgba(34,211,238,0.28), transparent 60%),
    radial-gradient(38% 38% at 82% 18%, rgba(167,139,250,0.27), transparent 65%),
    radial-gradient(46% 46% at 50% 85%, rgba(99,102,241,0.22), transparent 60%);
  filter: blur(42px);
  animation: blobFloat 36s ease-in-out infinite alternate;
  mix-blend-mode: screen;
}

/* 3) Drifting orbs (particles) */
.animated-bg .particles{ position:absolute; inset:-10% 0 0 0; }
.animated-bg .particles span{
  position:absolute; display:block;
  width:12px; height:12px; border-radius:999px;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.95), rgba(124,58,237,0.55));
  box-shadow: 0 0 20px rgba(124,58,237,0.35);
  opacity:.75;
  animation: floatParticle linear infinite;
}
/* positions/speeds */
.animated-bg .particles span:nth-child(1){ left:5%;  top:82%; animation-duration:38s; animation-delay:-2s; }
.animated-bg .particles span:nth-child(2){ left:12%; top:88%; animation-duration:44s; animation-delay:-8s; }
.animated-bg .particles span:nth-child(3){ left:22%; top:86%; animation-duration:32s; animation-delay:-16s; }
.animated-bg .particles span:nth-child(4){ left:31%; top:84%; animation-duration:36s; animation-delay:-4s; }
.animated-bg .particles span:nth-child(5){ left:39%; top:90%; animation-duration:40s; animation-delay:-14s; }
.animated-bg .particles span:nth-child(6){ left:46%; top:85%; animation-duration:34s; animation-delay:-10s; }
.animated-bg .particles span:nth-child(7){ left:54%; top:88%; animation-duration:42s; animation-delay:-6s; }
.animated-bg .particles span:nth-child(8){ left:62%; top:86%; animation-duration:35s; animation-delay:-18s; }
.animated-bg .particles span:nth-child(9){ left:69%; top:90%; animation-duration:39s; animation-delay:-12s; }
.animated-bg .particles span:nth-child(10){ left:76%; top:87%; animation-duration:33s; animation-delay:-20s; }
.animated-bg .particles span:nth-child(11){ left:83%; top:89%; animation-duration:41s; animation-delay:-9s; }
.animated-bg .particles span:nth-child(12){ left:91%; top:85%; animation-duration:37s; animation-delay:-3s; }
.animated-bg .particles span:nth-child(13){ left:18%; top:92%; width:8px; height:8px;  animation-duration:46s; animation-delay:-7s; }
.animated-bg .particles span:nth-child(14){ left:28%; top:94%; width:9px; height:9px;  animation-duration:43s; animation-delay:-5s; }
.animated-bg .particles span:nth-child(15){ left:48%; top:93%; width:8px; height:8px;  animation-duration:47s; animation-delay:-11s; }
.animated-bg .particles span:nth-child(16){ left:58%; top:95%; width:9px; height:9px;  animation-duration:45s; animation-delay:-15s; }
.animated-bg .particles span:nth-child(17){ left:72%; top:93%; width:7px; height:7px;  animation-duration:49s; animation-delay:-13s; }
.animated-bg .particles span:nth-child(18){ left:88%; top:94%; width:7px; height:7px;  animation-duration:48s; animation-delay:-1s; }

/* content above animations */
.block-container{ position:relative; z-index:1; padding-top:2rem; padding-bottom:5rem; }

/* Optional general glass style */
.glass{
  background: var(--card);
  border:1px solid var(--card-border);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  border-radius:18px; padding:1.25rem 1.25rem 1rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.35);
}

/* --- Glass wrapper specifically for the buttons row --- */
#btn-bar-anchor { display:none; }
div:has(> #btn-bar-anchor){
  background: var(--card);
  border: 1px solid var(--card-border);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 14px;
  padding: 0.8rem 0.8rem 0.6rem;
  margin: 0.75rem 0 1.25rem 0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}

/* Buttons polish */
.stButton>button, .stDownloadButton>button{
  border:1px solid var(--card-border);
  background: linear-gradient(180deg, rgba(124,58,237,.95), rgba(99,102,241,.95));
  color:#fff; font-weight:700; padding:.65rem 1rem; border-radius:12px;
  box-shadow:0 10px 24px rgba(124,58,237,.35);
}
.stButton>button:hover{ transform: translateY(-1px); }
.stDownloadButton>button{ background: linear-gradient(180deg,#22d3ee,#06b6d4); }

/* Animations */
@keyframes gradientShift{
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}
@keyframes blobFloat{
  0%  { transform: translate3d(-3%,-2%,0) scale(1.02) rotate(0deg); }
  50% { transform: translate3d( 3%, 3%,0) scale(1.06) rotate(8deg); }
  100%{ transform: translate3d( 6%,-1%,0) scale(1.03) rotate(-6deg); }
}
@keyframes floatParticle{
  0%   { transform: translate3d(0, 0, 0) scale(0.95); opacity:.0; }
  8%   { opacity:.75; }
  50%  { transform: translate3d(20px, -55vh, 0) scale(1.05); }
  100% { transform: translate3d(0, -110vh, 0) scale(0.95); opacity:.0; }
}
</style>

<!-- Inject animated layers -->
<div class="animated-bg">
  <div class="bg-gradient"></div>
  <div class="bg-blobs"></div>
  <div class="particles">
    <span></span><span></span><span></span><span></span><span></span><span></span>
    <span></span><span></span><span></span><span></span><span></span><span></span>
    <span></span><span></span><span></span><span></span><span></span><span></span>
  </div>
</div>
"""
st.markdown(ANIMATED_BG, unsafe_allow_html=True)

# --------------------------
# Sidebar: minimal settings (model/key inputs removed)
# --------------------------
st.sidebar.header("Settings")

mode = st.sidebar.radio(
    "Generation mode",
    ["Gemini","Offline (no AI key)"]
)

# Removed: model textbox + API key textbox.
# App now uses default model + GEMINI_API_KEY env var.
default_model = "gemini-1.5-flash"

num_cards = st.sidebar.slider("How many flashcards?", min_value=5, max_value=50, value=12, step=1)

# --------------------------
# Main UI
# --------------------------
st.title("🧠 AI Flashcard Maker")
st.write("Upload study material (PDF/DOCX/TXT) or paste text. Generate Q&A cards, then take a quiz.")

uploaded_files = st.file_uploader(
    "Upload files (optional)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)
pasted_text = st.text_area("Or paste your study text here", height=200, placeholder="Paste your notes, textbook chapter, etc...")

# === Glass-wrapped buttons row (Generate / Clear All) ===
btn_bar = st.container()
with btn_bar:
    # Invisible anchor so CSS can target THIS container with :has selector
    st.markdown('<div id="btn-bar-anchor"></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        gen_clicked = st.button("Generate Flashcards", use_container_width=True)
    with col_b:
        clear_clicked = st.button("Clear All", use_container_width=True)

# Actions for buttons (outside the container so UI stays stable)
if gen_clicked:
    content = extract_text_from_files(uploaded_files) + ("\n" + pasted_text if pasted_text else "")
    content = content.strip()
    if not content:
        st.error("Please upload a file or paste some text first.")
    else:
        try:
            if mode.startswith("Offline"):
                cards = generate_flashcards_offline(content, k=num_cards)
            else:
                # Use default Gemini model; API key must be set as env var GEMINI_API_KEY
                cards = generate_flashcards_gemini(content, model=default_model, k=num_cards)

            # Basic validation
            clean_cards = []
            for c in cards:
                q = (c.get("question") or "").strip()
                a = (c.get("answer") or "").strip()
                if q and a:
                    clean_cards.append({"question": q, "answer": a})
            if not clean_cards:
                st.warning("No cards generated. Try a different mode, more text, or another model.")
            else:
                st.session_state["cards"] = clean_cards
                st.success(f"Generated {len(clean_cards)} flashcards.")
        except Exception as e:
            st.exception(e)

if clear_clicked:
    for key in ["cards", "quiz_index", "quiz_score", "quiz_finished", "choices_cache", "review", "scored"]:
        st.session_state.pop(key, None)
    st.info("Cleared.")

cards: List[Dict[str, str]] = st.session_state.get("cards", [])

if cards:
    st.subheader("Generated Flashcards")
    with st.expander("Preview cards (Q/A)"):
        for i, c in enumerate(cards, start=1):
            st.markdown(f"**{i}. Q:** {c['question']}")
            st.markdown(f"**A:** {c['answer']}")
            st.markdown("---")

    # Download JSON
    json_bytes = json.dumps(cards, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button("Download as JSON", data=json_bytes, file_name="flashcards.json", mime="application/json")

    st.markdown("### Quiz Mode")

    # Initialize quiz state
    if "quiz_index" not in st.session_state:
        st.session_state.quiz_index = 0
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_finished" not in st.session_state:
        st.session_state.quiz_finished = False
    if "choices_cache" not in st.session_state:
        st.session_state.choices_cache = {}
    if "review" not in st.session_state:
        st.session_state.review = {}          # idx -> {"selected": str, "correct": bool}
    if "scored" not in st.session_state:
        st.session_state.scored = []          # list of idx already counted

    # Prepare current card
    idx = st.session_state.quiz_index
    if idx >= len(cards):
        st.session_state.quiz_finished = True

    if not st.session_state.quiz_finished:
        current = cards[idx]
        st.write(f"Question {idx+1} of {len(cards)}")
        st.markdown(f"**{current['question']}**")

        # Multiple-choice options (cached per index so it doesn't reshuffle on rerun)
        if idx not in st.session_state.choices_cache:
            st.session_state.choices_cache[idx] = build_mc_options(cards, idx, n=4)
        choices = st.session_state.choices_cache[idx]

        # Keep selection stable across reruns using a keyed widget
        sel = st.radio("Choose an answer:", options=choices, index=None, key=f"choice_{idx}")

        # Buttons side-by-side
        col1, col2 = st.columns([1, 1])
        with col1:
            check = st.button("Check Answer", key=f"check_{idx}", use_container_width=True)
        with col2:
            skip = st.button("Next Question ➡️", key=f"next_{idx}", use_container_width=True)

        # Handle "Check Answer" (do NOT advance here)
        if check:
            if sel is None:
                st.warning("Please choose an option.")
            else:
                is_correct = sel.strip() == current["answer"].strip()
                st.session_state.review[idx] = {"selected": sel, "correct": is_correct}
                if is_correct and idx not in st.session_state.scored:
                    st.session_state.quiz_score += 1
                    st.session_state.scored.append(idx)

        # Show feedback if this question was checked
        if idx in st.session_state.review:
            if st.session_state.review[idx]["correct"]:
                st.success("Correct! ✅")
            else:
                st.error(f"Incorrect ❌. Correct answer: {current['answer']}")

        # Handle "Next Question" (advance regardless of checked or not)
        if skip:
            st.session_state.quiz_index += 1
            if st.session_state.quiz_index >= len(cards):
                st.session_state.quiz_finished = True
            st.rerun()

    if st.session_state.quiz_finished:
        st.success(f"Quiz finished! Score: {st.session_state.quiz_score} / {len(cards)}")
        if st.button("Restart Quiz"):
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_finished = False
            st.session_state.choices_cache = {}
            st.session_state.review = {}
            st.session_state.scored = []
            st.rerun()
else:
    st.info("No cards yet. Upload or paste content, then click Generate Flashcards.")
