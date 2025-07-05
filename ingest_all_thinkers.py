import os
import re
from typing import List
from pathlib import Path
import psycopg2
from openai import OpenAI

# ✅ Set up OpenAI client (modern SDK)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ PostgreSQL DB connection settings
DB_CONFIG = {
    "dbname": "selahdevotional",
    "user": "selah",
    "password": "4HisGlory!",
    "host": "142.93.114.5",
    "port": 5432,
}

# ✅ Connect to the database
conn = psycopg2.connect(**DB_CONFIG, sslmode='disable')
cursor = conn.cursor()

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

# 🤖 Get embedding using new OpenAI SDK
def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    try:
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

# 🗄️ Insert one chunk into DB
def insert_chunk(book_title: str, chapter: str, chunk_index: int, chunk_text: str, embedding: List[float], author: str):
    cursor.execute("""
        INSERT INTO texts (book_title, chapter, chunk_index, chunk_text, embedding, author)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (book_title, chapter, chunk_index, chunk_text, embedding, author))
    conn.commit()

# 📥 Ingest one text file
def ingest_file(file_path: Path, author: str):
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
                insert_chunk(book_title, chapter_title, chunk_index, chunk, embedding, author)
                print(f"✅ Inserted chunk {chunk_index} of {chapter_title}")
                chunk_index += 1
            else:
                print(f"⚠️ Skipped chunk {chunk_index} due to embedding error")

# 🔁 Ingest all .txt files in all thinker folders
def ingest_all(base_dir: Path):
    for thinker_dir in base_dir.iterdir():
        if thinker_dir.is_dir():
            author = thinker_dir.name
            for file in thinker_dir.glob("*.txt"):
                try:
                    ingest_file(file, author)
                except Exception as e:
                    print(f"⚠️ Error with {file}: {e}")

# 🚀 Entry point
if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.resolve()
    ingest_all(BASE_DIR)
    cursor.close()
    conn.close()
    print("\n🎉 All thinkers ingested.")
