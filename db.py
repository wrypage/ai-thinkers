import os
from config import DB_PARAMS, OPENAI_API_KEY, OPENAI_PROJECT_ID
from openai import OpenAI
import psycopg

# ✅ Initialize OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    project=OPENAI_PROJECT_ID
)

# ✅ Get all thinkers from DB
def get_thinkers():
    with psycopg.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT author FROM texts ORDER BY author;")
            return [row[0] for row in cur.fetchall()]

# ✅ Get OpenAI embedding
def embed_text(text):
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding
    return embedding

# ✅ Search for similar chunks by vector distance
def search_similar_chunks(question, selected_thinkers, top_k=5):
    query_embedding = embed_text(question)

    # 🔁 Convert to PostgreSQL vector literal
    pg_vector = f"[{','.join(str(x) for x in query_embedding)}]"

    with psycopg.connect(**DB_PARAMS) as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            sql = """
                SELECT id, author, book_title, chapter, chunk_text,
                       embedding <=> %s::vector AS distance
                FROM texts
                WHERE author = ANY(%s)
                ORDER BY distance ASC
                LIMIT %s;
            """
            cur.execute(sql, (pg_vector, selected_thinkers if isinstance(selected_thinkers, list) else [selected_thinkers], top_k * len(selected_thinkers)))
            return cur.fetchall()
