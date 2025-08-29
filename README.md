AI Flashcard Maker (Gemini)
Turn your study material into exam-ready Q&A flashcards and drill them in a built-in quiz mode. Upload PDFs/DOCX/TXT or paste text → generate cards with Google Gemini (or a fast offline heuristic) → practice with multiple-choice and instant feedback. The app has a live animated background and glass UI for a pleasant study vibe.

✨ Features
* Two generators
    * Gemini (gemini-1.5-flash by default) for high-quality cards
    * Offline mode (no API key) for quick, local cards
* File & text input: PDF, DOCX, TXT, or plain pasted text
* Quiz mode: multiple choice, “Check Answer”, Next Question skip, final score
* Download: export the generated deck as JSON
* UI polish: animated gradient + floating blobs, glass panels, modern buttons
* Private by default: reads GEMINI_API_KEY from your environment (no key stored in the UI)

🧰 Tech Stack
* Python + Streamlit
* Google generative AI (Gemini API)
* pypdf, docx2txt for parsing PDFs/DOCX

🚀 Quick Start

# 1) Clone & enter
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
# 2) (Recommended) Virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
# 3) Install deps
pip install -r requirements.txt
# 4) (Optional) Enable Gemini mode
export GEMINI_API_KEY="YOUR_GEMINI_KEY"

# 5) Run
streamlit run app.py (or)
Open the local URL (usually http://localhost:8501).

🕹️ How to Use
1. Choose Generation mode in the sidebar: Offline or Gemini.
2. Upload one or more files (PDF/DOCX/TXT) or paste your text.
3. Click Generate Flashcards.
4. Review the cards (expand “Preview cards”) or Download as JSON.
5. Scroll to Quiz Mode → pick answers → Check Answer → Next Question ➡️.
6. See your final score and Restart Quiz any time.

⚙️ Configuration
* GEMINI_API_KEY: set as an environment variable to use Gemini mode.
    * macOS/Linux: export GEMINI_API_KEY="..."
    * Windows (PowerShell): setx GEMINI_API_KEY "..." (then reopen terminal)
* Default model: gemini-1.5-flash (can be changed in code if desired).

🧪 Offline vs Gemini
* Offline: quick, local heuristic that pulls definitional sentences and turns them into simple Q&A.
* Gemini: sends your content to Gemini and returns a clean JSON list of {question, answer} pairs for higher quality.

🎨 UI Customization
* Animated background + particles are pure CSS inside app.py.
    * Tweak speeds (e.g., animation-duration) or number/size of particles in the CSS block.
* The buttons bar uses a glass wrapper (via a tiny anchor + :has() selector) to keep Streamlit widgets inside a frosted panel.

📦 Output
* JSON file containing an array of { "question": "...", "answer": "..." }.

🛠️ Troubleshooting
* No cards generated → try more text, switch modes, or confirm your GEMINI_API_KEY.
* PDF text empty → some PDFs are scanned images; paste text or use a text-based PDF.
* Port in use → streamlit run app.py --server.port 8502.

🗺️ Roadmap
* Editable cards before quizzing
* CSV/Anki export
* Spaced-repetition practice
* OCR for scanned PDFs/images
