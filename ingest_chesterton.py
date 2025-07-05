import os
import re
import openai
import psycopg2
from typing import List, Optional

# Set your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database connection configuration (local on Droplet)
DB_CONFIG = {
    "dbname": "selahdevotional",
    "user": "selah",
    "password": "4HisGlory!",
    "host": "142.93.114.5",  # your droplet's public IP
    "port": 5432,
}

# Connect to PostgreSQL without SSL (local connection)
conn = psycopg2.connect(
    dbname=DB_CONFIG["dbname"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    sslmode='disable'  # SSL not required for localhost
)

cursor = conn.cursor()

def clean_gutenberg_text(text: str) -> str:
    start_match = re.search(r"\*\*\* START OF (THIS|THE) PROJECT GUTENBERG EBOOK .* \*\*\*", text)
    end_match = re.search(r"\*\*\* END OF (THIS|THE) PROJECT GUTENBERG EBOOK .* \*\*\*", text)

    if start_match and end_match:
        text = text[start_match.end():end_match.start()]
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def split_into_chapters(text: str) -> List[str]:
    chapters = re.split(r'\nCHAPTER [^\n]+\n', text, flags=re.IGNORECASE)
    if len(chapters) == 1:
        return [text]
    return chapters

def chunk_text(text: str, max_tokens=500) -> List[str]:
    words = text.split()
    chunks = []
    chunk = []
    count = 0
    for word in words:
        chunk.append(word)
        count += 1
        if count >= max_tokens:
            chunks.append(" ".join(chunk))
            chunk = []
            count = 0
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks

def get_embedding(text: str) -> List[float]:
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def insert_chunk(book_title: str, chapter_title: Optional[str], chunk_index: int,
                 chunk_text: str, embedding: List[float]):
    sql = """
    INSERT INTO texts (book_title, chapter, chunk_index, chunk_text, embedding)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (book_title, chapter_title, chunk_index, chunk_text, embedding))
    conn.commit()

def ingest_book(file_path: str, book_title: str):
    print(f"Starting ingestion for {book_title} from file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    print(f"Read {len(raw_text)} characters from {file_path}")

    clean_text = clean_gutenberg_text(raw_text)
    chapters = split_into_chapters(clean_text)

    print(f"Detected {len(chapters)} chapters")

    chunk_counter = 0
    for i, chapter_text in enumerate(chapters):
        chapter_title = f"Chapter {i+1}"
        chunks = chunk_text(chapter_text, max_tokens=500)
        for chunk in chunks:
            embedding = get_embedding(chunk)
            insert_chunk(book_title, chapter_title, chunk_counter, chunk, embedding)
            print(f"Inserted chunk {chunk_counter} of chapter {chapter_title}")
            chunk_counter += 1

    print(f"Finished ingestion for {book_title}")

if __name__ == "__main__":
    books = {
        "Orthodoxy": "orthodoxy.txt",
        "The Everlasting Man": "the-everlasting-man.txt",
        "Heretics": "heretics.txt",
        "What's Wrong with the World": "whats-wrong-with-the-world.txt",
        "The Outline of Sanity": "outline-of-sanity.txt",
    }
    for title, filepath in books.items():
        ingest_book(filepath, title)

    cursor.close()
    conn.close()
