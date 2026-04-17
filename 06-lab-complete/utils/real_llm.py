import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask(question: str, delay: float = 0.0) -> str:
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": question}],
        max_tokens=int(os.getenv("MAX_TOKENS", "500")),
        temperature=0.7,
    )
    return response.choices[0].message.content


def ask_stream(question: str):
    stream = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": question}],
        max_tokens=int(os.getenv("MAX_TOKENS", "500")),
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
