import os
import re
from pathlib import Path
from typing import List
from dotenv import load_dotenv

import psycopg
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_PROJECT_ID, DB_PARAMS

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    project=OPENAI_PROJECT_ID
)

# 🧼 Clean up raw text
def clean_text(text: str) -> str:
    text = re.sub(r"\*\*\* START OF (THIS|THE) PROJECT GUTENBERG EBOOK .* \*\*\*", "", text)
    text = re.sub(r"\*\*\* END OF (THIS|THE) PROJECT GUTENBERG EBOOK .* \*\*\*", "", text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# 📚 Split into chapters
def split_into_chapters(text: str) -> List[str]:
    chapters = re.split(r'\n+CHAPTER [^\n]+\n+', text, flags=re.IGNORECASE)
    return chapters if len(chapters) > 1 else [text]

# ✂️ Break into chunks
def chunk_text(text: str, max_words=500) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

# 🤖 Get embedding from OpenAI
def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    try:
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

# 🗄️ Insert one chunk into the database
def insert_chunk(cur, book_title: str, chapter: str, chunk_index: int, chunk_text: str, embedding: List[float], author: str):
    cur.execute("""
        INSERT INTO texts (book_title, chapter, chunk_index, chunk_text, embedding, author)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (book_title, chapter, chunk_index, chunk_text, embedding, author))

# 📥 Ingest one text file
def ingest_file(cur, file_path: Path, author: str):
    book_title = file_path.stem.replace("_", " ").title()
    print(f"\n📘 Ingesting: {book_title} by {author}")

    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    clean = clean_text(raw)
    chapters = split_into_chapters(clean)
    print(f"🔹 Detected {len(chapters)} chapter(s)")

    chunk_index = 0
    for i, chapter in enumerate(chapters):
        chapter_title = f"Chapter {i+1}" if len(chapters) > 1 else "Full Text"
        chunks = chunk_text(chapter)
        for chunk in chunks:
            embedding = get_embedding(chunk)
            if embedding:
                insert_chunk(cur, book_title, chapter_title, chunk_index, chunk, embedding, author)
                print(f"✅ Inserted chunk {chunk_index} of {chapter_title}")
                chunk_index += 1
            else:
                print(f"⚠️ Skipped chunk {chunk_index} due to embedding error")

# 🔁 Ingest all .txt files in thinker folders
def ingest_all(base_dir: Path):
    with psycopg.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cur:
            for thinker_dir in base_dir.iterdir():
                if thinker_dir.is_dir():
                    author = thinker_dir.name
                    for file in thinker_dir.glob("*.txt"):
                        try:
                            ingest_file(cur, file, author)
                            conn.commit()
                        except Exception as e:
                            print(f"⚠️ Error with {file}: {e}")

# 🚀 Entry point
if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.resolve()
    ingest_all(BASE_DIR)
    print("\n🎉 All thinkers ingested.")
