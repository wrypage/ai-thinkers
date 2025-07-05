import gradio as gr
from query_logic import answer_query
from db import get_thinkers

def ask(question, selected_thinkers, mode):
    if not question.strip():
        return "Please enter a question."
    return answer_query(question, selected_thinkers, mode)

thinkers = get_thinkers()

with gr.Blocks() as demo:
    gr.Markdown("## Ask Christian Thinkers")
    with gr.Row():
        question = gr.Textbox(label="Your Question", lines=2)
        mode = gr.Radio(
            ["Modern paraphrase", "Show direct quotes"],
            value="Modern paraphrase",
            label="Mode"
        )
    selected = gr.CheckboxGroup(choices=thinkers, label="Choose Thinkers", value=thinkers)
    ask_btn = gr.Button("Ask")
    output = gr.Textbox(label="Answer", lines=20, show_copy_button=True)

    ask_btn.click(fn=ask, inputs=[question, selected, mode], outputs=output)

if __name__ == "__main__":
    demo.launch()