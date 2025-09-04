from ui import build_ui

if __name__ == "__main__":
    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=10000)
