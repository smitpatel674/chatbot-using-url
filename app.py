import os
from ui import build_ui

if __name__ == "__main__":
    demo = build_ui()
    port = int(os.environ.get("PORT", 7860))  # Render provides PORT
    demo.launch(server_name="0.0.0.0", server_port=port, share=False, show_api=False)
