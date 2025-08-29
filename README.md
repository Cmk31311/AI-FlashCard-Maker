# AI Flashcard Maker (Streamlit)

Upload study material (PDF/DOCX/TXT) or paste text, generate Q&A flashcards, and take a quiz.

## 1) Prerequisites
- Python 3.10+ installed

## 2) Setup
```bash
# Create project folder
mkdir ai-flashcard-maker && cd ai-flashcard-maker

# (Recommended) Create a virtual environment
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Copy this repo's files into the folder (or unzip the provided zip)
# Then install deps:
pip install -r requirements.txt
```

## 3) (Optional) OpenAI setup for better cards
Set your API key (only needed for OpenAI mode):
```bash
# macOS/Linux (temporary for this terminal):
export OPENAI_API_KEY="YOUR_KEY_HERE"

# Windows PowerShell (persistent):
setx OPENAI_API_KEY "YOUR_KEY_HERE"
# then close and reopen terminal
```

## 4) Run the app
```bash
streamlit run app.py
```

Open the URL shown in the terminal (usually http://localhost:8501).

## 5) Use it
- Upload PDFs/DOCX/TXT or paste text.
- Choose "Offline" or "OpenAI" in the sidebar.
- Click "Generate Flashcards".
- Scroll to "Quiz Mode" to practice answers.
- Download your cards as JSON.

## Notes
- Offline mode uses simple heuristics, fine for quick practice.
- OpenAI mode yields higher-quality questions/answers.
