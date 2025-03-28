# src/models/tot_agent.py

from src.models.openai_interface import call_openai_with_tracking

def generate_thoughts_openai(prompt, model="gpt-3.5-turbo", temperature=0.3):
    messages = [
        {"role": "system", "content": "You are an expert evaluator of RFP proposals."},
        {"role": "user", "content": prompt}
    ]
    return call_openai_with_tracking(messages, model=model, temperature=temperature)
