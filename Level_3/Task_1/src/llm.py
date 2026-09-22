import ollama

from config import HISTORY_LIMIT, OLLAMA_BASE_URL, OLLAMA_MODEL

# ------------------------------------------------------------------
# System prompt (prompt engineering)
# Defines the assistant's personality, honesty rules, and limits.
# ------------------------------------------------------------------

SYSTEM_PROMPT = """You are a smart, friendly AI assistant built as an \
AI/ML internship project at RaushByte Technologies. You are the \
conversational part of an assistant that also has a separate Python \
tool layer.

How to behave:
- Be helpful, professional, concise and friendly.
- Give clear, beginner-friendly answers. Keep them short (a few \
sentences or a short list) unless the user asks for more detail.
- Be accurate. If you are unsure about something, say so honestly \
instead of guessing.
- Use the conversation history to understand follow-up questions such \
as "explain it simply" or "give me an example".

Strict limitations you MUST respect:
- You cannot see the current date or time. If the user asks for the \
time or date, tell them to ask directly, e.g. "what time is it?" or \
"what is today's date?" — the tool layer will answer with the real value.
- You cannot open websites, search the web, create files, or read \
files. Those actions are handled by the tool layer when the user gives \
a direct command such as "open github", "search python tutorials", or \
"create a note called ideas.txt with: ...".
- NEVER claim you performed an action, and never pretend an action \
succeeded. If a request is unsafe or unsupported, politely refuse and \
suggest what the assistant can do.
"""


# ------------------------------------------------------------------
# Client & connection check
# ------------------------------------------------------------------

def create_client() -> ollama.Client:
    """Create an Ollama client pointing at the configured base URL."""
    return ollama.Client(host=OLLAMA_BASE_URL)


def _installed_model_names(client: ollama.Client) -> list:
    """Return installed model names (handles both old and new
    ollama-package response formats)."""
    result = client.list()
    try:
        return [model.model for model in result.models]      # newer versions
    except AttributeError:
        return [model["name"] for model in result["models"]]  # older versions


def _model_is_available(names: list, wanted: str) -> bool:
    """True if the wanted model (or a matching tag of it) is installed."""
    if wanted in names:
        return True
    base = wanted.split(":")[0]
    return any(name.split(":")[0] == base for name in names)


def check_connection(client: ollama.Client):
    """Check Ollama and the configured model. Returns (ok, message).

    Not fatal: even when this fails, the Python tool layer still
    works — only question answering needs the model.
    """
    try:
        names = _installed_model_names(client)
    except Exception:
        return False, (f"Could not connect to Ollama at {OLLAMA_BASE_URL}. "
                       "Is Ollama running? Start it with 'ollama serve' or "
                       "launch the Ollama app, then restart the assistant.")

    if _model_is_available(names, OLLAMA_MODEL):
        return True, f"Connected to Ollama — model '{OLLAMA_MODEL}' is ready."

    available = ", ".join(names) if names else "none"
    return False, (f"Model '{OLLAMA_MODEL}' is not installed yet "
                   f"(installed: {available}). "
                   f"Pull it with:  ollama pull {OLLAMA_MODEL}")


# ------------------------------------------------------------------
# Question answering with conversation memory
# ------------------------------------------------------------------

def generate_reply(client: ollama.Client, history: list) -> str:
    """Send the system prompt + recent history to the local LLM and
    return the reply (or a friendly error message)."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # history is already capped by the controller; slicing again is
    # defense in depth.
    messages += history[-HISTORY_LIMIT:]

    try:
        response = client.chat(model=OLLAMA_MODEL, messages=messages)
    except Exception:
        return ("I'm having trouble reaching the local AI model. Please "
                "check that Ollama is running and the model "
                f"'{OLLAMA_MODEL}' is installed. (Tool commands still work.)")

    content = response.message.content
    if content and content.strip():
        return content.strip()
    return "I'm sorry — the model returned an empty response. Please try rephrasing."