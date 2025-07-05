import psycopg2
import psycopg2.extras
from config import DB_PARAMS
from openai import OpenAI

client = OpenAI()

def get_thinkers():
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT author FROM texts ORDER BY author;")
            return [row[0] for row in cur.fetchall()]

def embed_text(text):
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return embedding.data[0].embedding

def search_similar_chunks(question, selected_thinkers, top_k=5):
    query_embedding = embed_text(question)
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = """
                SELECT id, author, book, chapter, text,
                       embedding <=> %s AS distance
                FROM texts
                WHERE author = ANY(%s)
                ORDER BY distance ASC
                LIMIT %s;
            """
            cur.execute(sql, (query_embedding, selected_thinkers, top_k * len(selected_thinkers)))
            return cur.fetchall()