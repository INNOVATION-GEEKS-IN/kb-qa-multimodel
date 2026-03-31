# 📖 Multi-Model Knowledge Base Q&A

A production-ready Q&A app over your product/technical docs — powered by **5 LLMs** you can switch between in real time.

| Model | Provider | Type |
|-------|----------|------|
| Claude (claude-sonnet-4) | Anthropic | Cloud API |
| Gemini (gemini-1.5-flash) | Google | Cloud API |
| Grok (grok-3) | xAI | Cloud API |
| Groq (llama-3.3-70b) | Groq | Cloud API (fast) |
| Ollama (llama3.2) | Local | Runs on your machine |

**Stack:** Python · Flask · ChromaDB (vector search) · Multi-model routing

---

## Architecture

```
docs/                         ← your .txt / .md files
  └── productx_api.md
  
app.py                        ← Flask web server + routes
kb.py                         ← ChromaDB indexing + semantic search
models.py                     ← Multi-model router (Claude/Gemini/Grok/Groq/Ollama)
templates/index.html          ← Web UI with model switcher

.chromadb/                    ← auto-created local vector store
```

### How it works (RAG pipeline)
```
User question
     ↓
ChromaDB semantic search → top 5 relevant chunks from your docs
     ↓
Chunks + question sent to chosen LLM as context
     ↓
LLM answers strictly from your docs
     ↓
Answer + source files shown in UI
```

---

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/kb-qa-multimodel.git
cd kb-qa-multimodel
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API keys
```bash
cp .env.example .env
```
Open `.env` and fill in the keys you have. You only need keys for the models you want to use.

| Key | Where to get it |
|-----|----------------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey |
| `GROK_API_KEY` | https://console.x.ai |
| `GROQ_API_KEY` | https://console.groq.com |
| Ollama | No key — install from https://ollama.com, then run `ollama pull llama3.2` |

### 5. Add your docs
Drop any `.txt` or `.md` files into the `docs/` folder.
A sample product API doc is already there to test with.

### 6. Run the app
```bash
python app.py
```
Open **http://localhost:5000** in your browser.

---

## Usage

1. **Select a model** in the left sidebar
2. **Type your question** in the chat box
3. The app searches your docs semantically, sends relevant chunks to the model, and shows the answer
4. **Source files** used to answer are shown below each response
5. After adding new docs, click **↻ Re-index Docs** in the header

---

## Project Structure

```
kb-qa-multimodel/
├── app.py                  # Flask app, routes
├── kb.py                   # ChromaDB knowledge base
├── models.py               # Claude / Gemini / Grok / Groq / Ollama
├── requirements.txt
├── .env.example            # Copy to .env, fill your keys
├── .gitignore
├── docs/
│   └── productx_api.md     # Sample doc — replace with your own
└── templates/
    └── index.html          # Web UI
```

---

## Pushing to GitHub

```bash
git init
git add .
git commit -m "initial commit: multi-model KB Q&A app"
git remote add origin https://github.com/YOUR_USERNAME/kb-qa-multimodel.git
git branch -M main
git push -u origin main
```

> ⚠️ Make sure `.env` is in `.gitignore` before pushing — never commit API keys!

---

## What You Learn From This Project

| Concept | Where in code |
|---------|--------------|
| Anthropic Messages API | `models.py` → `ask_claude()` |
| Gemini API | `models.py` → `ask_gemini()` |
| OpenAI-compatible APIs (Grok) | `models.py` → `ask_grok()` |
| Groq fast inference | `models.py` → `ask_groq()` |
| Local LLMs via Ollama | `models.py` → `ask_ollama()` |
| RAG (chunking + vector search) | `kb.py` |
| ChromaDB embeddings | `kb.py` → `KnowledgeBase` |
| System prompts & prompt engineering | `models.py` → `SYSTEM_PROMPT` |
| Flask backend + REST API | `app.py` |
| Async frontend with fetch() | `templates/index.html` |

---

## Next Level Upgrades

- [ ] **File upload UI** — drag & drop docs directly in the browser
- [ ] **Chat history** — maintain conversation context across turns
- [ ] **Model comparison** — ask the same question to all models side by side
- [ ] **Streaming responses** — show answer word-by-word as it generates
- [ ] **Better chunking** — semantic/markdown-aware splitting
- [ ] **Deploy to cloud** — Railway, Render, or Docker

---

## License
MIT
