# Use OpenAI function for creating embeddings for tool descriptions and examples.

from openai import OpenAI
import os
from src.utils.logging_utils import log_openai_call
import inspect

client = OpenAI()  # uses your environment variable OPENAI_API_KEY

def get_openai_embedding(text, model="text-embedding-ada-002", source=None):
    """
    Get OpenAI embedding for a given text.
    """
    response = client.embeddings.create(
        model=model,
        input=[text]
    )

    # Find source of which function called call_openai_with_tracking()
    if source is None:
        for frame in inspect.stack()[1:]:
            module = inspect.getmodule(frame.frame)
            if module and not module.__name__.startswith("utils.logging_utils"):
                source = frame.function
                break
        else:
            source = "unknown"
    
    log_openai_call(text, response, source=source, embedding=True)
    return response.data[0].embedding
