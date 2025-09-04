from ui import build_ui

app = build_ui()  # 👈 expose this for gunicorn

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8080)
