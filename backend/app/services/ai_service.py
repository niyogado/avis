import os

import requests
from dotenv import load_dotenv

load_dotenv()

EJOCHAT_API_URL = os.getenv("EJOCHAT_API_URL")
EJOCHAT_API_KEY = os.getenv("EJOCHAT_API_KEY")

# The EjoChat proxy injects its own system prompt (a Kinyarwanda "Subiza"
# assistant instructed to answer concisely). Without an explicit system
# message, long structured outputs get truncated mid-JSON and values can
# come back in Kinyarwanda instead of English. Sending our own system
# message overrides those defaults for AVIS tasks.
DEFAULT_SYSTEM_PROMPT = (
    "You are AVIS, an AI career assistant inside the AVIS platform. "
    "Always respond in English, regardless of any other language instruction. "
    "Be accurate and never invent information about the user."
)

# ---------------------------------------------------------------------------
# Provider registry. Only providers/models AVIS has tested are exposed —
# the frontend may offer these choices but never arbitrary model names, and
# API keys stay server-side at all times.
# ---------------------------------------------------------------------------
SUPPORTED_MODELS: dict[str, list[str]] = {
    "ejochat": ["ejo-chat"],
    "huggingface": [
        "meta-llama/Llama-3.1-8B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3",
    ],
}

PROVIDERS = ("auto", "ejochat", "huggingface")
RESPONSE_STYLES = ("concise", "balanced", "detailed")

_STYLE_INSTRUCTIONS = {
    "concise": "Keep answers short and to the point (a few sentences unless asked otherwise).",
    "balanced": "Balance brevity and completeness; use short lists where helpful.",
    "detailed": "Give thorough, well-structured answers with concrete steps and examples.",
}

HF_INFERENCE_URL_TEMPLATE = "https://api-inference.huggingface.co/models/{model}"


def provider_available(name: str) -> bool:
    """Server-side availability check (secrets never leave the backend)."""
    if name == "ejochat":
        return bool(EJOCHAT_API_URL and EJOCHAT_API_KEY)
    if name == "huggingface":
        return bool(HUGGINGFACE_API_KEY)
    return False


def _system_with_style(system: str | None, style: str) -> str:
    base = DEFAULT_SYSTEM_PROMPT if system is None else system
    instruction = _STYLE_INSTRUCTIONS.get((style or "balanced").lower())
    if not instruction:
        return base
    return f"{base}\nResponse style: {instruction}"


def _call_ejochat(message: str, system: str | None) -> str:
    if not EJOCHAT_API_URL or not EJOCHAT_API_KEY:
        raise ValueError("EjoChat is not configured on this server.")
    headers = {
        "X-API-Key": EJOCHAT_API_KEY,
        "Content-Type": "application/json",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": message})
    response = requests.post(
        EJOCHAT_API_URL,
        headers=headers,
        json={"messages": messages},
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _call_huggingface(message: str, system: str | None, model: str | None) -> str:
    if not HUGGINGFACE_API_KEY:
        raise ValueError("Hugging Face is not configured on this server.")
    chosen = model if model in SUPPORTED_MODELS["huggingface"] else SUPPORTED_MODELS["huggingface"][0]
    prompt = f"{system}\n\nUser: {message}\nAssistant:" if system else message
    response = requests.post(
        HF_INFERENCE_URL_TEMPLATE.format(model=chosen),
        headers={
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "inputs": prompt,
            "parameters": {"max_new_tokens": 700, "return_full_text": False},
            "options": {"wait_for_model": True},
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    # HF Inference returns either a plain string or a list of generations.
    if isinstance(data, list) and data:
        first = data[0]
        text = first.get("generated_text") if isinstance(first, dict) else str(first)
        return (text or "").strip()
    if isinstance(data, dict):
        return str(data.get("generated_text") or "").strip()
    return str(data).strip()


def chat_with_ai(
    message: str,
    system: str | None = None,
    provider: str = "auto",
    model: str | None = None,
    style: str = "balanced",
    allow_fallback: bool = True,
):
    """Call the configured AI provider with automatic fallback.

    - provider 'auto'   -> EjoChat primary, Hugging Face backup.
    - explicit provider  -> that provider; falls back to the other when
      `allow_fallback` is set and it fails.
    - style adjusts response-length guidance via the system prompt.
    Raises ValueError with a safe message when every configured option fails.
    """
    resolved_system = _system_with_style(system, style)

    if provider not in PROVIDERS:
        raise ValueError(f"Unsupported AI provider '{provider}'.")

    if provider == "auto":
        chain = ["ejochat", "huggingface"]
    elif provider == "ejochat":
        chain = ["ejochat"] + (["huggingface"] if allow_fallback else [])
    else:
        chain = ["huggingface"] + (["ejochat"] if allow_fallback else [])

    last_error: Exception | None = None
    for name in chain:
        if not provider_available(name):
            continue
        try:
            if name == "ejochat":
                return _call_ejochat(message, resolved_system)
            return _call_huggingface(message, resolved_system, model)
        except Exception as exc:  # noqa: BLE001 - try the next provider
            last_error = exc
            continue

    if last_error is not None:
        raise ValueError("The AI service is temporarily unavailable. Please try again shortly.") from last_error
    raise ValueError("No AI provider is configured on this server.")