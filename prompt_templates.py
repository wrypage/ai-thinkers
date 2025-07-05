def get_prompt_for_thinker(thinker, question, chunks):
    quote_block = "\n\n".join(f"- {c['text']}" for c in chunks)
    base_prompt = f"""
You are paraphrasing {thinker} in modern English. Your task is to rewrite the following excerpts as if {thinker} were answering the user's question today.

Preserve the thinker's unique style, theology, and logic. Do NOT summarize or explain. Do NOT add your own thoughts. Only express the ideas in updated language faithful to their tone.

User's question: "{question}"

Excerpts:
{quote_block}

Now write {thinker}’s answer in modern English:
"""
    return base_prompt.strip()