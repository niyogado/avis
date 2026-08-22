import os

import requests
from dotenv import load_dotenv

load_dotenv()

EJOCHAT_API_URL = os.getenv("EJOCHAT_API_URL")
EJOCHAT_API_KEY = os.getenv("EJOCHAT_API_KEY")


def chat_with_ai(message: str):
    if not EJOCHAT_API_URL:
        raise ValueError("EJOCHAT_API_URL is not configured")

    if not EJOCHAT_API_KEY:
        raise ValueError("EJOCHAT_API_KEY is not configured")

    headers = {
        "X-API-Key": EJOCHAT_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ]
    }

    response = requests.post(
        EJOCHAT_API_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]