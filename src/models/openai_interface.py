# openai_interface.py – Handles all OpenAI API interactions

import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from src.utils.logging_utils import log_phase, log_openai_call, log_openai_call_time
import time

# Load the .env file
load_dotenv()

# Get the API key
my_openai_api_key = os.getenv("OPENAI_API_KEY")

# Safety check
if not my_openai_api_key:
    raise OpenAIError("❌ OPENAI_API_KEY not set. Please check your .env file or environment variables.")

# Create OpenAI client
client = OpenAI(api_key=my_openai_api_key)


def call_openai_with_tracking(messages, model="gpt-3.5-turbo", temperature=0.7, max_tokens=500):
    """
    Calls OpenAI's ChatCompletion API with structured messages and tracks token usage and estimated cost.

    Parameters:
    messages (list): A list of message dictionaries, where each dictionary contains 'role' and 'content' keys.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.7.
    max_tokens (int): The maximum number of tokens to generate in the completion. Default is 500.

    Workflow:
    1. The function takes the input parameters and calls the OpenAI ChatCompletion API.
    2. The API returns a response containing multiple choices and token usage information.
    3. The function extracts the content of the first choice from the response.
    4. It updates the total tokens used and the estimated cost in USD.
    5. It logs the prompt tokens, completion tokens, total tokens used so far, and the estimated cost.

    Returns:
    str: The content of the first choice from the API response.
    """
    global total_tokens_used, estimated_cost_usd

    total_tokens_used = 0
    estimated_cost_usd = 0.0
    COST_PER_1K_TOKENS = 0.0015

    try:
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        duration = round(time.time() - start, 2)
    except Exception as e:
        return f"⚠️ Tool execution error: {str(e)}"

    # Extract token usage and calculate estimated cost
    usage = response.usage
    prompt_tokens = usage.prompt_tokens or 0
    completion_tokens = usage.completion_tokens or 0
    total = usage.total_tokens or (prompt_tokens + completion_tokens)

    # Update tracking
    total_tokens_used += total
    estimated_cost_usd += (total / 1000) * COST_PER_1K_TOKENS

    # Logging
    log_openai_call(messages, response, prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens)
    log_openai_call_time(duration)

    return response.choices[0].message.content.strip()
