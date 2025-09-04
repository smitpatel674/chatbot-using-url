import os
import gradio as gr

def respond(message):
    return "You said: " + message

app = gr.Blocks()

with app:
    txt = gr.Textbox(label="Enter message")
    out = gr.Textbox(label="Response")
    txt.submit(respond, txt, out)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.launch(server_name="0.0.0.0", server_port=port)
