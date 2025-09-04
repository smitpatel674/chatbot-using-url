import gradio as gr
from actions import action_crawl, action_chat, action_clear

def build_ui():
    with gr.Blocks(title="Website Chatbot (Gemini)", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🔎 Website Chatbot — Gemini + Gradio")

        with gr.Row():
            url_inp = gr.Textbox(label="Website URL", placeholder="https://example.com")
            crawl_btn = gr.Button("Crawl & Index", variant="primary")

        with gr.Row():
            max_pages = gr.Slider(5, 100, value=20, step=1, label="Max pages")
            max_depth = gr.Slider(0, 4, value=2, step=1, label="Max depth")
            lang_choice = gr.Dropdown(["English", "Hindi", "Gujarati"], value="English", label="Chat Language")

        status = gr.Markdown("")
        sidebar = gr.Textbox(label="Indexed pages (sample)", interactive=False, lines=8)

        chat = gr.Chatbot(label="Chat", height=450, show_copy_button=True, type="messages")
        msg = gr.Textbox(placeholder="Ask a question about the site…", label="Your message")

        with gr.Row():
            send = gr.Button("Send", variant="primary")
            clear = gr.Button("Clear Chat")

        info = gr.Markdown(visible=False)

        crawl_btn.click(action_crawl, [url_inp, max_pages, max_depth, lang_choice], [info, chat, status, sidebar])
        send.click(action_chat, [msg, chat], [msg, chat])
        msg.submit(action_chat, [msg, chat], [msg, chat])
        clear.click(action_clear, None, [chat, info])

    return demo
