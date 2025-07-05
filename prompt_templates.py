# prompt_templates.py

def get_prompt_for_thinker(thinker_name, question, quotes, mode="paraphrase"):
    """
    Construct a thinker-specific prompt using retrieved quote chunks.
    mode = 'paraphrase' for natural synthesis, 'quote' for literal references.
    """
    quote_text = "\n\n".join(f"{i+1}. {q['text']}" for i, q in enumerate(quotes))

    if mode == "quote":
        return (
            f"You are {thinker_name}, a historical Christian thinker. Below are excerpts from your writings that may relate to the user's question.\n\n"
            f"Quotes:\n{quote_text}\n\n"
            f"Now answer the following question using only these quotes where appropriate.\n\n"
            f"Question: {question}"
        )
    else:
        return (
            f"You are {thinker_name}, a historical Christian thinker. Based on your known writings and the quotes below, provide a thoughtful, paraphrased answer to the user’s question.\n\n"
            f"Quotes:\n{quote_text}\n\n"
            f"Question: {question}"
        )
