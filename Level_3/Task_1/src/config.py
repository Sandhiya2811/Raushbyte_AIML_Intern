import os
from pathlib import Path

# Load .env if python-dotenv is installed (it is in requirements.txt,
# but the app still works without it using these defaults).
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

# ------------------------------------------------------------------
# Paths — anchored to this file, so no machine-specific paths exist
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent      # the Task_1 folder
NOTES_DIR = BASE_DIR / "data" / "notes"                # the ONLY writable folder

# ------------------------------------------------------------------
# Ollama / LLM settings
# ------------------------------------------------------------------

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Short-term conversational memory: how many recent messages are kept.
try:
    HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "16"))
except ValueError:
    HISTORY_LIMIT = 16        # fall back if .env contains a non-number

# ------------------------------------------------------------------
# Safety whitelist — the only websites the assistant may open
# ------------------------------------------------------------------

ALLOWED_WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "linkedin": "https://www.linkedin.com",
}