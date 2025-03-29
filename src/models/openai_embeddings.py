# Use OpenAI function for creating embeddings for tool descriptions and examples.

from openai import OpenAI
import os

client = OpenAI()  # uses your environment variable OPENAI_API_KEY

def get_openai_embedding(text, model="text-embedding-ada-002"):
    response = client.embeddings.create(
        model=model,
        input=[text]
    )
    return response.data[0].embedding
