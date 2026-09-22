import re
from typing import NamedTuple, Optional

import llm
import tools
from config import HISTORY_LIMIT

# ------------------------------------------------------------------
# Banner and help text
# ------------------------------------------------------------------

BANNER = """====================================================
               SMART AI ASSISTANT
====================================================

Powered by:
Local LLM (Ollama) + Python Tools

Type 'help' to see available commands.
Type 'exit' to quit.
"""

HELP_TEXT = """Available capabilities:

• Answer general questions
• Maintain short-term conversation context
• Tell date and time
• Open approved websites
• Perform browser searches
• Create notes
• Read notes
• List notes

Type 'exit' to close the assistant."""

# ------------------------------------------------------------------
# Intent detection phrases (matched on cleaned, lowercase text)
# ------------------------------------------------------------------

EXIT_PHRASES = ["exit", "quit", "bye", "goodbye", "stop"]
HELP_PHRASES = ["help", "commands", "what can you do", "capabilities"]

TIME_PHRASES = ["what time", "whats the time", "what is the time",
                "tell me the time", "current time", "the time please",
                "time please", "time now", "what time is it"]

DATE_PHRASES = ["what date", "whats the date", "what is the date",
                "todays date", "current date", "tell me the date",
                "what is today", "date today"]

LIST_NOTES_PHRASES = ["list notes", "show notes", "list my notes",
                      "show my notes", "what are my notes",
                      "which notes do i have"]

POLITE_PREFIXES = ("please ", "could you ", "can you ", "would you ")

OPEN_PREFIXES = ("open ", "launch ", "go to ", "take me to ", "visit ")
SEARCH_PREFIXES = ("search for ", "search ", "google ", "look up ")

# --- Note command patterns -----------------------------------------
# "create a note called interview.txt with: Revise Python and SQL"
CREATE_NOTE_WITH_NAME = re.compile(
    r"^(?:create|make|take)\s+(?:a\s+)?note\s+called\s+"
    r"(?P<name>[\w\-.]+)\s+"
    r"(?:with|saying|containing|that\s+says)\s*:?\s*(?P<content>.+)$",
    re.IGNORECASE)

# "create a note: buy milk" / "take a note saying call mom"
# (separator is REQUIRED so questions like "how do I create a note in
#  notepad?" are not mistaken for commands)
CREATE_NOTE_PLAIN = re.compile(
    r"^(?:create|make|take)\s+(?:a\s+)?note\s*"
    r"(?::|with|saying|containing|that\s+says)\s*:?\s*(?P<content>.+)$",
    re.IGNORECASE)

# "create a note" with nothing after it -> tool shows usage guidance
NOTE_INTENT_HINT = re.compile(
    r"^(?:create|make|take)\s+(?:a\s+)?note\b", re.IGNORECASE)

# "read the note called ideas" / "read note ideas.txt"
READ_NOTE_NAMED = re.compile(
    r"(?:read|show|open)\s+(?:the\s+)?note\s+(?:called\s+)?(?P<name>[\w\-.]+)",
    re.IGNORECASE)

# "read interview.txt" (a .txt filename identifies a note on its own)
READ_NOTE = re.compile(
    r"(?:read|show)\s+(?:the\s+)?(?:note\s+)?(?:called\s+)?(?P<name>[\w\-.]+\.txt)",
    re.IGNORECASE)


# ------------------------------------------------------------------
# Text helpers (whole-word matching — reused from my Level 1 chatbot)
# ------------------------------------------------------------------

def _clean_for_matching(text: str) -> str:
    """Lowercase-ish copy with punctuation removed — used ONLY for
    phrase matching. (Arguments are extracted from the original text,
    so filenames like 'notes.txt' keep their dots.)"""
    text = text.replace("'", "").replace("\u2019", "")   # what's -> whats
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text)
    return " ".join(cleaned.lower().split())


def _contains_phrase(phrase: str, text: str) -> bool:
    """Whole-word matching: 'time' will NOT match inside 'sometimes'."""
    return f" {phrase} " in f" {text} "


def _strip_politeness(text: str) -> str:
    """Remove leading 'please / can you / could you' so commands like
    'please open github' still match the 'open' prefix."""
    text = text.strip()
    changed = True
    while changed:
        changed = False
        lowered = text.lower()
        for prefix in POLITE_PREFIXES:
            if lowered.startswith(prefix):
                text = text[len(prefix):].strip()
                changed = True
    return text


# ------------------------------------------------------------------
# Intent detection
# ------------------------------------------------------------------

class Intent(NamedTuple):
    kind: str                    # "exit" | "help" | "tool" | "question"
    tool_name: Optional[str]
    arguments: object = None


def detect_intent(text: str) -> Intent:
    """Classify a user message as exit / help / a tool call / a question.

    Order matters:
      - exit first (always works)
      - notes BEFORE websites/time so 'open note X' and
        'create a note about time management' route correctly
      - search BEFORE time so 'search for time management' is a search
      - time/date use SPECIFIC phrases so questions like
        'what is time complexity?' stay with the LLM
    """
    text = _strip_politeness(text)
    match_text = _clean_for_matching(text)

    # 1. Exit and help
    if any(_contains_phrase(p, match_text) for p in EXIT_PHRASES):
        return Intent("exit", None)
    if any(_contains_phrase(p, match_text) for p in HELP_PHRASES):
        return Intent("help", None)

    # 2. Notes
    named = CREATE_NOTE_WITH_NAME.search(text)
    if named:
        return Intent("tool", "create_note",
                      {"filename": named.group("name"),
                       "content": named.group("content")})
    plain = CREATE_NOTE_PLAIN.search(text)
    if plain:
        return Intent("tool", "create_note",
                      {"filename": None, "content": plain.group("content")})
    if NOTE_INTENT_HINT.search(text):
        return Intent("tool", "create_note",
                      {"filename": None, "content": None})   # -> guidance
    read_match = READ_NOTE_NAMED.search(text) or READ_NOTE.search(text)
    if read_match:
        return Intent("tool", "read_note", read_match.group("name"))
    if any(_contains_phrase(p, match_text) for p in LIST_NOTES_PHRASES):
        return Intent("tool", "list_notes", None)

    # 3. Websites and web search
    lowered = text.lower()
    for prefix in OPEN_PREFIXES:
        if lowered.startswith(prefix):
            target = text[len(prefix):].strip().strip(" .!?,")
            if target.startswith("the "):
                target = target[4:]
            return Intent("tool", "open_website", target)
    for prefix in SEARCH_PREFIXES:
        if lowered.startswith(prefix):
            return Intent("tool", "search_web",
                          text[len(prefix):].strip())

    # 4. Time and date (specific phrases only)
    if any(_contains_phrase(p, match_text) for p in TIME_PHRASES):
        return Intent("tool", "get_current_time", None)
    if any(_contains_phrase(p, match_text) for p in DATE_PHRASES):
        return Intent("tool", "get_current_date", None)

    # 5. Everything else -> the LLM answers, using conversation memory
    return Intent("question", None)


# ------------------------------------------------------------------
# Message handling (shared by console UI and Streamlit UI)
# ------------------------------------------------------------------

def handle_user_message(text: str, client, history: list):
    """Process one user message. Returns (reply, should_exit)."""
    if not text.strip():
        return ("Please type a message, or type 'help' for available "
                "commands."), False

    intent = detect_intent(text)
    if intent.kind == "exit":
        return "Goodbye! Have a great day.", True

    # Store the user message FIRST so the LLM sees it as the latest turn
    history.append({"role": "user", "content": text.strip()})

    if intent.kind == "help":
        reply = HELP_TEXT
    elif intent.kind == "tool":
        # Deterministic, safe execution — result shown verbatim
        reply = tools.execute_tool(intent.tool_name, intent.arguments)
    else:
        reply = llm.generate_reply(client, history)

    # Short-term conversational memory: keep only the most recent
    # HISTORY_LIMIT messages (the list never grows without bound)
    history.append({"role": "assistant", "content": reply})
    del history[:-HISTORY_LIMIT]

    return reply, False


# ------------------------------------------------------------------
# Console interface
# ------------------------------------------------------------------

def main() -> None:
    """Start the console assistant."""
    print(BANNER)

    client = llm.create_client()
    ok, message = llm.check_connection(client)
    print(f"Model status : {message}")
    if not ok:
        print("Note: question answering needs the model, but tool commands")
        print("(time, date, websites, search, notes) still work.\n")

    history = []
    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nAssistant: Goodbye! Have a great day.")
            break

        reply, should_exit = handle_user_message(user_input, client, history)
        print(f"Assistant: {reply}\n")
        if should_exit:
            break


if __name__ == "__main__":
    main()