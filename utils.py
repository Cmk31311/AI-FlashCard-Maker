import io
import os
import json
import random
import re
from typing import List, Dict

# -------------------------------
# File parsing
# -------------------------------
def _read_txt(file) -> str:
    try:
        return file.read().decode("utf-8", errors="ignore")
    except Exception:
        file.seek(0)
        return file.read().decode("latin-1", errors="ignore")

def _read_pdf(file) -> str:
    try:
        from pypdf import PdfReader
    except Exception as e:
        raise RuntimeError("pypdf is not installed. Add it in requirements.txt") from e

    file.seek(0)
    reader = PdfReader(file)
    text = []
    for page in reader.pages:
        try:
            text.append(page.extract_text() or "")
        except Exception:
            pass
    return "\n".join(text)

def _read_docx(file) -> str:
    try:
        import docx2txt
    except Exception as e:
        raise RuntimeError("docx2txt is not installed. Add it in requirements.txt") from e

    # docx2txt needs a path; write to temp
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file.read())
        tmp.flush()
        path = tmp.name
    try:
        return docx2txt.process(path) or ""
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

def extract_text_from_files(files) -> str:
    if not files:
        return ""
    texts = []
    for f in files:
        name = (getattr(f, 'name', '') or "").lower()
        if name.endswith(".pdf"):
            texts.append(_read_pdf(f))
        elif name.endswith(".docx"):
            texts.append(_read_docx(f))
        elif name.endswith(".txt"):
            texts.append(_read_txt(f))
        else:
            # Fallback try text
            texts.append(_read_txt(f))
    return "\n\n".join([t for t in texts if t])

# -------------------------------
# Flashcard generation - OFFLINE
# -------------------------------
def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def simple_sentence_split(text: str) -> List[str]:
    # crude splitter
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [normalize_whitespace(p) for p in parts if normalize_whitespace(p)]

def extract_key_facts(sentences: List[str], k: int) -> List[str]:
    # pick sentences that look definitional or important
    scored = []
    for s in sentences:
        score = 0
        if " is " in s.lower() or " are " in s.lower():
            score += 3
        if ":" in s:
            score += 1
        if len(s) > 80:
            score += 1
        if len(s) > 140:
            score += 1
        scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [s for _, s in scored[: max(k*2, k+3)]]
    # dedupe while preserving order
    seen = set()
    uniq = []
    for s in top:
        if s not in seen:
            uniq.append(s); seen.add(s)
    return uniq[:k]

def sentence_to_qa(s: str) -> Dict[str, str]:
    m = re.search(r"^(.+?)\s+is\s+(.+)$", s, flags=re.IGNORECASE)
    if m:
        subj = normalize_whitespace(m.group(1))
        desc = normalize_whitespace(m.group(2).rstrip(". "))
        return {"question": f"What is {subj}?", "answer": desc}
    return {"question": f"What is the key idea of: \"{s[:140]}\"?", "answer": s}

def generate_flashcards_offline(text: str, k: int = 12) -> List[Dict[str, str]]:
    text = normalize_whitespace(text)
    if not text:
        return []
    sentences = simple_sentence_split(text)
    facts = extract_key_facts(sentences, k)
    cards = [sentence_to_qa(s) for s in facts]
    return cards[:k]

# -------------------------------
# Flashcard generation - GEMINI
# -------------------------------
def generate_flashcards_gemini(text: str, model: str = "gemini-1.5-flash", k: int = 12) -> List[Dict[str, str]]:
    """
    Requires env var GEMINI_API_KEY. Uses Google Generative AI (Gemini) to get JSON array of {question, answer}.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Set it in the sidebar or as an environment variable.")

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gen_model = genai.GenerativeModel(model or "gemini-1.5-flash")

    prompt = f"""
You are a helpful assistant that creates study flashcards.
Given the study material below, return EXACTLY a JSON array of {k} objects, each with keys "question" and "answer".
- Questions should be clear and concise (<= 120 chars).
- Answers should be short, factual (<= 250 chars), no markdown.
- Do NOT include explanations or any text outside the JSON array.

STUDY MATERIAL:
{text[:120000]}
    """.strip()

    response = gen_model.generate_content(prompt)
    raw = getattr(response, "text", "") or ""
    # Try to extract JSON array safely
    start = raw.find("["); end = raw.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Gemini response did not contain a valid JSON array. Raw response:\n" + raw[:500])

    data = json.loads(raw[start:end+1])
    cards = []
    for item in data:
        q = str(item.get("question", "")).strip()
        a = str(item.get("answer", "")).strip()
        if q and a:
            cards.append({"question": q, "answer": a})
    return cards[:k]

# -------------------------------
# Quiz utilities
# -------------------------------
def build_mc_options(cards: List[Dict[str, str]], correct_index: int, n: int = 4) -> List[str]:
    """
    Return n options: 1 correct + (n-1) random incorrect answers.
    """
    correct = cards[correct_index]["answer"]
    pool = [c["answer"] for i, c in enumerate(cards) if i != correct_index and c.get("answer")]
    random.shuffle(pool)
    opts = [correct] + pool[: max(0, n-1)]
    random.shuffle(opts)
    # Ensure unique strings and fill if not enough unique distractors
    seen = set(); uniq = []
    for o in opts:
        if o not in seen:
            uniq.append(o); seen.add(o)
    while len(uniq) < n:
        uniq.append(correct)
    return uniq[:n]
