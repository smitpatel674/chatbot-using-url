from ui import build_ui

app = build_ui()  # ✅ expose for gunicorn

if __name__ == "__main__":
    app.launch(share=False, show_api=False, inbrowser=True)
