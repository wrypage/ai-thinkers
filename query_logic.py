# query_logic.py
from prompt_templates import get_prompt_for_thinker
from db import search_similar_chunks


def build_messages(thinker_name, question, mode="paraphrase"):
    """
    Constructs OpenAI chat messages using thinker-specific logic.
    mode: 'paraphrase' (default) or 'quote' controls how the answer is structured.
    """
    search_results = search_similar_chunks(question, thinker_name)
    prompt = get_prompt_for_thinker(thinker_name, question, search_results, mode)

    messages = [
        {"role": "system", "content": "You are a helpful assistant generating answers in the voice of a Christian thinker."},
        {"role": "user", "content": prompt}
    ]
    return messages
