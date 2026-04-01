"""
Multi-Model Knowledge Base Q&A App
====================================
Supports: Claude, Gemini, Grok, Groq, Ollama
Vector search powered by ChromaDB

Run:
    python app.py
Open: http://localhost:5000
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from kb import KnowledgeBase
from models import get_answer

load_dotenv()

app = Flask(__name__)
kb = KnowledgeBase(docs_folder="docs")
ALLOWED_EXTENSIONS = {".txt", ".md"}


@app.route("/")
def index():
    docs = kb.list_docs()
    models = [
        {"id": "claude",  "name": "Claude",        "provider": "Anthropic", "color": "#c97a3a"},
        {"id": "gemini",  "name": "Gemini",         "provider": "Google",    "color": "#1a73e8"},
        {"id": "grok",    "name": "Grok",           "provider": "xAI",       "color": "#1a1a1a"},
        {"id": "groq",    "name": "Groq",           "provider": "Groq",      "color": "#f55036"},
        {"id": "ollama",  "name": "Ollama (local)", "provider": "Local",     "color": "#2d6a4f"},
    ]
    return render_template("index.html", docs=docs, models=models)


@app.route("/ask", methods=["POST"])
def ask():
    data     = request.get_json()
    question = data.get("question", "").strip()
    model_id = data.get("model", "claude")

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    # Retrieve relevant chunks from vector DB
    chunks = kb.search(question, n_results=5)

    if not chunks:
        return jsonify({
            "answer": "No documents found. Please add .txt or .md files to the docs/ folder and re-index.",
            "sources": []
        })

    context   = "\n\n".join([c["text"] for c in chunks])
    sources   = list({c["source"] for c in chunks})

    answer = get_answer(question, context, model_id)
    return jsonify({"answer": answer, "sources": sources, "model": model_id})


@app.route("/index-docs", methods=["POST"])
def index_docs():
    count = kb.index_docs()
    return jsonify({"message": f"Indexed {count} document(s) successfully."})


@app.route("/upload-docs", methods=["POST"])
def upload_docs():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files uploaded."}), 400

    os.makedirs(kb.docs_folder, exist_ok=True)
    saved_files = []
    skipped_files = []

    for file in files:
        filename = secure_filename(file.filename or "")
        ext = os.path.splitext(filename)[1].lower()

        if not filename:
            continue
        if ext not in ALLOWED_EXTENSIONS:
            skipped_files.append(filename)
            continue

        target_path = os.path.join(kb.docs_folder, filename)
        file.save(target_path)
        saved_files.append(filename)

    if not saved_files:
        return jsonify({
            "error": "No supported files uploaded. Only .txt and .md are allowed.",
            "skipped": skipped_files,
        }), 400

    return jsonify({
        "message": f"Uploaded {len(saved_files)} file(s) to docs.",
        "uploaded": saved_files,
        "skipped": skipped_files,
    })


@app.route("/docs-status")
def docs_status():
    return jsonify({"docs": kb.list_docs(), "total_chunks": kb.total_chunks()})


if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    print("Multi-Model KB Q&A starting...")
    print("Add .txt/.md files to docs/ then click 'Re-index Docs' in the UI")
    print("Open http://localhost:5000")
    print(kb.index_docs())   # auto-index on startup
    app.run(debug=True, host="0.0.0.0", port=5000)
