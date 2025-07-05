import openai
from db import search_similar_chunks
from prompt_templates import get_prompt_for_thinker
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def answer_query(question, selected_thinkers, mode="Modern paraphrase"):
    if not selected_thinkers:
        return "Please select at least one thinker."

    results = search_similar_chunks(question, selected_thinkers, top_k=5)
    if not results:
        return "No relevant quotes found."

    if mode == "Show direct quotes":
        return format_quotes(results)

    responses = []
    for thinker in selected_thinkers:
        thinker_chunks = [r for r in results if r['author'] == thinker]
        if not thinker_chunks:
            continue

        prompt = get_prompt_for_thinker(thinker, question, thinker_chunks)
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            response = f"### {thinker}\n" + completion.choices[0].message.content.strip()
            responses.append(response)
        except Exception as e:
            responses.append(f"Error processing {thinker}: {e}")

    return "\n\n---\n\n".join(responses)

def format_quotes(results):
    formatted = []
    for r in results:
        text = r['text']
        author = r['author']
        book = r.get('book', 'Unknown book')
        chapter = r.get('chapter', '')
        reference = f"{book}, {chapter}".strip(', ')
        formatted.append(f"**{author} ({reference})**: {text}")
    return "\n\n".join(formatted)