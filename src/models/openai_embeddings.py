# Use OpenAI function for creating embeddings for tool descriptions and examples.

from openai import OpenAI
import os
from src.utils.logging_utils import log_openai_call

client = OpenAI()  # uses your environment variable OPENAI_API_KEY

def get_openai_embedding(text, model="text-embedding-ada-002"):
    response = client.embeddings.create(
        model=model,
        input=[text]
    )
    log_openai_call(text, response)
    return response.data[0].embedding
