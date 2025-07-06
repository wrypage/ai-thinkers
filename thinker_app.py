import os
from dotenv import load_dotenv
load_dotenv()  # Must be first

from openai import OpenAI
import gradio as gr
from config import OPENAI_API_KEY
from thinker_profiles import THINKER_PROFILES
from query_logic import build_messages

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project=os.getenv("OPENAI_PROJECT_ID")
)


def ask_thinker(thinker_key, question, mode):
    if thinker_key not in THINKER_PROFILES:
        return f"Thinker '{thinker_key}' not found."

    messages = build_messages(thinker_key, question, mode=mode)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content


def run_interface():
    thinkers = sorted([(v["full_name"], k) for k, v in THINKER_PROFILES.items()])
    interface = gr.Interface(
        fn=ask_thinker,
        inputs=[
            gr.Dropdown(choices=thinkers, label="Choose a Thinker"),
            gr.Textbox(lines=3, placeholder="Enter your question here"),
            gr.Radio(choices=["paraphrase", "quote"], value="paraphrase", label="Response Style")
        ],
        outputs="text",
        title="Ask a Christian Thinker",
        description="Ask a theological or spiritual question and receive a response in the voice of a historic Christian thinker."
    )
    interface.launch()


if __name__ == "__main__":
    run_interface()
