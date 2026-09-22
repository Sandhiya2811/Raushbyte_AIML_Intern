import datetime
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Optional

from config import ALLOWED_WEBSITES, NOTES_DIR

# Characters never allowed in a note filename (covers Windows rules,
# path separators, and '..' style tricks)
INVALID_FILENAME_CHARS = '<>:"/\\|?*'


# ------------------------------------------------------------------
# Filename safety helpers
# ------------------------------------------------------------------

def _is_valid_filename(name: str) -> bool:
    """True only for a safe single filename (no paths, no spaces)."""
    name = name.strip()
    if not name or name in {".", ".."}:
        return False
    if " " in name or any(ch in INVALID_FILENAME_CHARS for ch in name):
        return False
    if name.startswith(".") or name.endswith("."):
        return False
    if any(ord(ch) < 32 for ch in name):        # control characters
        return False
    return True


def _safe_note_path(filename: str) -> Optional[Path]:
    """Join a filename to the notes folder and verify the result stays
    inside it (defense in depth against path tricks)."""
    candidate = (NOTES_DIR / filename).resolve()
    if candidate.parent != NOTES_DIR.resolve():
        return None
    return candidate


def _normalize_note_name(filename: str) -> str:
    """Clean a spoken/typed note name and ensure it ends with .txt."""
    filename = filename.strip().rstrip(".")       # drop sentence periods
    if not filename.lower().endswith(".txt"):
        filename += ".txt"
    return filename


# ------------------------------------------------------------------
# Date & time tools (real values from the system clock — the LLM
# is never asked to guess these)
# ------------------------------------------------------------------

def get_current_time() -> str:
    """Return the current time from the live system clock."""
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p').lstrip('0')}."


def get_current_date() -> str:
    """Return today's date from the live system clock."""
    today = datetime.date.today()
    return f"Today's date is {today.strftime('%d %B %Y').lstrip('0')}."


# ------------------------------------------------------------------
# Browser tools
# ------------------------------------------------------------------

def open_website(name: str) -> str:
    """Open an APPROVED website. Untrusted input can only reach this
    function as a lookup key in the whitelist — never as a URL."""
    name = (name or "").lower().strip().strip(" .!?,")
    if name.startswith("the "):
        name = name[4:]
    url = ALLOWED_WEBSITES.get(name)
    if url is None:
        allowed = ", ".join(ALLOWED_WEBSITES)
        return (f"Sorry, '{name or 'that'}' is not an approved website. "
                f"I can only open: {allowed}.")
    webbrowser.open(url)
    return f"Opening {name.capitalize()} in your browser."


def search_web(query: str) -> str:
    """Open a Google search page in the browser.

    HONESTY NOTE: this is browser-opening automation only. The
    assistant does NOT retrieve, read, or verify any web results.
    """
    query = (query or "").strip()
    if not query:
        return ("What would you like me to search for? "
                "Try: search python tutorials")
    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    webbrowser.open(url)
    return f"Opening a Google search for '{query}' in your browser."


# ------------------------------------------------------------------
# Notes tools (restricted to data/notes/, never overwrite)
# ------------------------------------------------------------------

def create_note(filename: Optional[str], content: Optional[str]) -> str:
    """Save a note inside data/notes/. Refuses to overwrite."""
    if not content or not content.strip():
        return ("It looks like the note content is missing. Try: "
                "create a note called ideas.txt with: your text here")

    content = content.strip()
    if filename:
        filename = _normalize_note_name(filename)
        if not _is_valid_filename(filename):
            return ("Sorry, that is not a valid note filename. Use letters, "
                    "numbers, dots, hyphens or underscores — no spaces and "
                    "no path separators.")
    else:
        # No name given -> use an automatic timestamped name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"note_{timestamp}.txt"

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    path = _safe_note_path(filename)
    if path is None:
        return "Sorry, that note filename is not allowed."

    if path.exists():
        return (f"A note called '{filename}' already exists, so I did NOT "
                f"overwrite it. Read it with 'read note {filename}' or "
                f"choose a different name.")

    try:
        path.write_text(content + "\n", encoding="utf-8")
    except OSError:
        return (f"I couldn't save the note '{filename}' — a file system "
                f"error occurred, so nothing was written.")
    return f"I've saved your note as '{filename}'.\nContent: {content}"


def read_note(filename: str) -> str:
    """Read a note from data/notes/ and return its content."""
    filename = _normalize_note_name(filename or "")
    if not _is_valid_filename(filename):
        return "Sorry, that is not a valid note filename."

    path = _safe_note_path(filename)
    if path is None:
        return "Sorry, that note filename is not allowed."
    if not path.exists():
        return (f"I couldn't find a note called '{filename}'. "
                f"Type 'list notes' to see your saved notes.")

    try:
        content = path.read_text(encoding="utf-8").strip()
    except OSError:
        return f"I couldn't read the note '{filename}' — a file system error occurred."
    return f"Here is your note '{filename}':\n\n{content}"


def list_notes() -> str:
    """List every saved note in data/notes/."""
    try:
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        notes = sorted(p.name for p in NOTES_DIR.iterdir()
                       if p.is_file() and p.suffix == ".txt")
    except OSError:
        return "Sorry, I couldn't read the notes folder."

    if not notes:
        return ("You have no saved notes yet. Create one with: "
                "create a note called ideas.txt with: your text here")
    listing = "\n".join(f"{i}. {name}" for i, name in enumerate(notes, start=1))
    return f"Your saved notes:\n{listing}"


# ------------------------------------------------------------------
# Tool router — keeps tool execution completely separate from the LLM
# ------------------------------------------------------------------

def execute_tool(tool_name: str, arguments) -> str:
    """Run a predefined tool by name and return its result message."""
    try:
        if tool_name == "get_current_time":
            return get_current_time()
        if tool_name == "get_current_date":
            return get_current_date()
        if tool_name == "open_website":
            return open_website(arguments or "")
        if tool_name == "search_web":
            return search_web(arguments or "")
        if tool_name == "create_note":
            args = arguments or {}
            return create_note(args.get("filename"), args.get("content"))
        if tool_name == "read_note":
            return read_note(arguments or "")
        if tool_name == "list_notes":
            return list_notes()
        return f"Unknown tool: {tool_name}"
    except Exception as error:
        # Safety net: friendly message, no traceback (and no unsafe action)
        return (f"Something went wrong while running that tool "
                f"({type(error).__name__}). No unsafe action was taken.")