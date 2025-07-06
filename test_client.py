from openai import OpenAI

client = OpenAI(
    api_key="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"
)

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="test"
)

print("✅ SUCCESS! Vector starts with:", response.data[0].embedding[:5])
