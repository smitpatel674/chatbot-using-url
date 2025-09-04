from state import STATE
from crawler import SiteKB
from gemini_client import init_gemini, build_system_prompt, compose_grounding_context, gemini_chat

def action_crawl(url: str, max_pages: int, max_depth: int, lang: str):
    STATE.reset()
    STATE.model = init_gemini("gemini-1.5-flash")
    STATE.language = lang

    if not url:
        return "", [], "Please enter a URL.", None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    STATE.kb = SiteKB(seed_url=url, max_pages=max_pages, max_depth=max_depth)
    STATE.kb.crawl()

    if not STATE.kb.pages:
        return "", [], "Could not crawl site or no text found.", None

    sidebar = "\n".join(f"- {p.title} ({p.url})" for p in STATE.kb.pages[:5])
    welcome = f"✅ Indexed {len(STATE.kb.pages)} pages from {STATE.kb.seed_url}.\nAsk me anything about this site!"
    return welcome, [], f"Crawled {len(STATE.kb.pages)} pages.", sidebar

def action_chat(message: str, chat_history: list):
    if STATE.model is None:
        STATE.model = init_gemini(STATE.model_name)

    sys_prompt = build_system_prompt(STATE.kb.seed_url if STATE.kb else "(no site)", STATE.language)
    grounding = compose_grounding_context(STATE.kb.retrieve(message, 6)) if STATE.kb else ""

    bot = gemini_chat(STATE.model, sys_prompt, STATE.history, message, grounding)
    STATE.history.append((message, bot))
    return "", chat_history + [{"role": "user", "content": message}, {"role": "assistant", "content": bot}]

def action_clear():
    STATE.history = []
    return [], ""
