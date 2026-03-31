"""
models.py — Multi-model router
================================
Supported models:
  - claude   → Anthropic Claude (claude-sonnet-4-20250514)
  - gemini   → Google Gemini   (gemini-1.5-flash)
  - grok     → xAI Grok        (grok-3)
  - groq     → Groq Cloud      (llama-3.3-70b-versatile)
  - ollama   → Local Ollama    (llama3.2 or any installed model)

Each function receives (question, context) and returns a string answer.
"""

import os

SYSTEM_PROMPT = """You are a helpful technical documentation assistant.
Answer questions using ONLY the provided context from the knowledge base.
- Be concise, clear, and accurate.
- If the answer is not in the context, say "I couldn't find that in the documentation."
- Cite the source document when possible.
- Do not use outside knowledge beyond what is provided."""


def _user_message(question: str, context: str) -> str:
    return f"""Context from knowledge base:
{context}

---
Question: {question}"""


# ------------------------------------------------------------------ #
#  Claude (Anthropic)                                                  #
# ------------------------------------------------------------------ #
def ask_claude(question: str, context: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model      = "claude-sonnet-4-20250514",
        max_tokens = 1024,
        system     = SYSTEM_PROMPT,
        messages   = [{"role": "user", "content": _user_message(question, context)}],
    )
    return response.content[0].text


# ------------------------------------------------------------------ #
#  Gemini (Google)                                                     #
# ------------------------------------------------------------------ #
def ask_gemini(question: str, context: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model    = genai.GenerativeModel(
        model_name     = "gemini-1.5-flash",
        system_instruction = SYSTEM_PROMPT,
    )
    response = model.generate_content(_user_message(question, context))
    return response.text


# ------------------------------------------------------------------ #
#  Grok (xAI)  — OpenAI-compatible endpoint                           #
# ------------------------------------------------------------------ #
def ask_grok(question: str, context: str) -> str:
    from openai import OpenAI
    client = OpenAI(
        api_key  = os.environ["GROK_API_KEY"],
        base_url = "https://api.x.ai/v1",
    )
    response = client.chat.completions.create(
        model    = "grok-3",
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": _user_message(question, context)},
        ],
    )
    return response.choices[0].message.content


# ------------------------------------------------------------------ #
#  Groq (fast inference cloud)                                         #
# ------------------------------------------------------------------ #
def ask_groq(question: str, context: str) -> str:
    from groq import Groq
    client   = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model    = "llama-3.3-70b-versatile",
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": _user_message(question, context)},
        ],
    )
    return response.choices[0].message.content


# ------------------------------------------------------------------ #
#  Ollama (local)                                                      #
# ------------------------------------------------------------------ #
def ask_ollama(question: str, context: str) -> str:
    import requests
    ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    payload = {
        "model":  ollama_model,
        "prompt": f"{SYSTEM_PROMPT}\n\n{_user_message(question, context)}",
        "stream": False,
    }
    resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"]


# ------------------------------------------------------------------ #
#  Router                                                              #
# ------------------------------------------------------------------ #
ROUTERS = {
    "claude": ask_claude,
    "gemini": ask_gemini,
    "grok":   ask_grok,
    "groq":   ask_groq,
    "ollama": ask_ollama,
}


def get_answer(question: str, context: str, model_id: str) -> str:
    fn = ROUTERS.get(model_id)
    if not fn:
        return f"Unknown model '{model_id}'. Choose from: {', '.join(ROUTERS.keys())}"
    try:
        return fn(question, context)
    except KeyError as e:
        key = str(e).strip("'")
        return f"⚠️ Missing API key: {key}. Add it to your .env file."
    except Exception as e:
        return f"⚠️ Error from {model_id}: {str(e)}"
