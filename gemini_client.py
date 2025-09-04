import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def init_gemini(model_name: str = "gemini-1.5-flash"):
    if not API_KEY:
        raise RuntimeError("❌ GEMINI_API_KEY not found in .env")
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(model_name)

def build_system_prompt(site_url: str, lang: str) -> str:
    prompts = {
        "English": "Answer in clear and professional English.",
        "Hindi": "उत्तर स्पष्ट और सरल हिंदी में दें।",
        "Gujarati": "સ્પષ્ટ અને સરળ ગુજરાતી ભાષામાં જવાબ આપો."
    }
    return f"You are an expert assistant for {site_url}.\n{prompts.get(lang, 'Answer in English.')}"

def compose_grounding_context(snippets, max_chars: int = 6000) -> str:
    out, used, total = [], set(), 0
    for ch, src in snippets:
        entry = f"\nSOURCE: {src}\nCONTENT:\n{ch}\n"
        if (src, ch[:80]) in used or total + len(entry) > max_chars:
            continue
        out.append(entry)
        used.add((src, ch[:80]))
        total += len(entry)
    return "\n".join(out)

def gemini_chat(model, system_prompt, history, user_msg, grounding):
    history_text = "\n".join([f"User: {u}\nAssistant: {a}" for u, a in history[-8:]])
    prompt = (
        f"SYSTEM:\n{system_prompt}\n\n"
        f"SITE CONTEXT:\n{grounding}\n\n"
        f"RECENT CHAT:\n{history_text}\n\n"
        f"USER:\n{user_msg}\n\n"
        "Answer clearly."
    )
    resp = model.generate_content(prompt)
    return resp.text.strip() if hasattr(resp, "text") and resp.text else "(No response)"
