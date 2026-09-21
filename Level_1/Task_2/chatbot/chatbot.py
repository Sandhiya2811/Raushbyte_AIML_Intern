
import random
import string

# =====================================================================
# 1. CHATBOT IDENTITY & GENERAL SETTINGS
# =====================================================================

BOT_NAME = "ByteBot"
ORGANIZATION = "RaushByte Technologies"

# Phrases that end the conversation
EXIT_PHRASES = ["bye", "exit", "quit", "goodbye"]

# Response when the input is not understood
FALLBACK_RESPONSE = (
    "I'm sorry, I don't understand that yet. Please try asking about "
    "AI, Machine Learning, Python, or internships - or type 'help' to "
    "see what I can do."
)

# Response when the user sends an empty message
EMPTY_INPUT_RESPONSE = "Please enter a message."

# Possible farewell messages (one is chosen at random)
FAREWELL_RESPONSES = [
    "Goodbye! Have a great day.",
    "Bye! Thanks for chatting with me.",
    "Goodbye! I hope you learned something new today.",
]

# =====================================================================
# 2. RULES
# Each rule is one topic the chatbot knows about.
#   - patterns : phrases to look for in the user's input
#   - responses: possible replies (one is chosen at random)
# Rules are checked from top to bottom - the FIRST match wins.
# =====================================================================

RULES = [
    {
        "name": "greeting",
        "patterns": ["hello", "hi", "hey",
                     "good morning", "good afternoon", "good evening"],
        "responses": [
            "Hello! Nice to meet you. How can I help you today?",
            "Hi there! What would you like to know?",
            "Hey! Feel free to ask me about AI, Machine Learning, or Python.",
        ],
    },
    {
        "name": "introduction",
        "patterns": ["who are you", "what are you", "introduce yourself"],
        "responses": [
            f"I am {BOT_NAME}, a simple rule-based chatbot created using "
            f"Python. I was built for the AI/ML internship at "
            f"{ORGANIZATION}."
        ],
    },
    {
        "name": "bot_name",
        "patterns": ["your name", "tell me your name"],
        "responses": [
            f"My name is {BOT_NAME}! I am a rule-based chatbot "
            f"written in Python."
        ],
    },
    {
        "name": "help",
        "patterns": ["help", "what can you do", "commands"],
        "responses": [
            "Here is what I can help you with:\n"
            "  1. Greet me            (hello / hi / hey)\n"
            "  2. 'who are you?'      or  'what is your name?'\n"
            "  3. 'what is AI?'\n"
            "  4. 'what is machine learning?'\n"
            "  5. 'what is Python?'\n"
            "  6. 'what is an internship?'\n"
            "  7. 'what is RaushByte?'\n"
            "  8. 'thank you'\n"
            "  9. End the chat        (bye / exit / quit / goodbye)"
        ],
    },
    {
        "name": "artificial_intelligence",
        "patterns": ["what is ai", "artificial intelligence",
                     "explain ai", "ai"],
        "responses": [
            "Artificial Intelligence (AI) is the ability of machines or "
            "computer systems to perform tasks that normally require "
            "human intelligence, such as understanding language, "
            "recognizing images, and making decisions."
        ],
    },
    {
        "name": "machine_learning",
        "patterns": ["what is machine learning", "machine learning",
                     "explain machine learning", "what is ml", "ml"],
        "responses": [
            "Machine Learning (ML) is a branch of AI in which computers "
            "learn patterns from data instead of being programmed with "
            "fixed rules. For example, a spam filter learns to detect "
            "spam by studying thousands of example emails."
        ],
    },
    {
        "name": "python",
        "patterns": ["what is python", "python", "tell me about python"],
        "responses": [
            "Python is a high-level, easy-to-learn programming language. "
            "It is widely used in AI, Machine Learning, Data Science, "
            "web development, and automation."
        ],
    },
    {
        "name": "internship",
        "patterns": ["internship", "what is an internship",
                     "tell me about internship"],
        "responses": [
            "An internship is a short-term work opportunity that helps "
            "students and beginners gain real-world, practical experience "
            "in a company. This chatbot is part of the AI/ML internship "
            f"at {ORGANIZATION}."
        ],
    },
    {
        "name": "organization",
        "patterns": ["raushbyte", "raushbyte technologies"],
        "responses": [
            f"{ORGANIZATION} is the organization hosting this AI/ML "
            "internship program. I was created for Level 1 - Task 2: "
            "Basic Chatbot Build. Since I am a rule-based chatbot, I "
            "only know what my programmer taught me - for official "
            "company information, please refer to RaushByte "
            "Technologies' official channels."
        ],
    },
    {
        "name": "gratitude",
        "patterns": ["thank you", "thanks", "thank you chatbot"],
        "responses": [
            "You're welcome! Is there anything else I can help you with?",
            "Happy to help! Feel free to ask anything else.",
        ],
    },
    {
        "name": "how_are_you",
        "patterns": ["how are you", "how are you doing"],
        "responses": [
            "I'm doing great, thank you for asking! I'm a simple "
            "program, so every day is a good day. How can I help you?"
        ],
    },
]

# =====================================================================
# 3. INPUT PROCESSING
# =====================================================================

def clean_input(user_input):
    """
    Prepare user input for matching:
      1. Convert to lowercase  -> 'HELLO' becomes 'hello'
      2. Remove extra spaces   -> '  hi  ' becomes 'hi'
      3. Remove punctuation    -> 'hello!' becomes 'hello'
    This makes matching case-insensitive and tolerant of
    extra spaces and punctuation.
    """
    cleaned = user_input.lower().strip()
    cleaned = cleaned.translate(str.maketrans("", "", string.punctuation))
    cleaned = " ".join(cleaned.split())   # collapse multiple spaces
    return cleaned


def matches_pattern(pattern, cleaned_input):
    """
    Return True if 'pattern' appears in the input as a WHOLE word
    or phrase (not inside another word).

    We surround both strings with spaces, so:
        pattern 'hi'  matches  'hi there'   -> True
        pattern 'hi'  does NOT match 'this' -> False
        pattern 'ai'  does NOT match 'train'-> False
    This simple trick gives us word-boundary matching without regex.
    """
    padded_input = f" {cleaned_input} "
    padded_pattern = f" {pattern} "
    return padded_pattern in padded_input

# =====================================================================
# 4. RESPONSE SELECTION (THE RULE-BASED "BRAIN")
# =====================================================================

def get_response(user_input):
    """
    Decide the chatbot's reply for a given input.

    Returns a tuple: (response, should_exit)
      - response    : the message to show the user
      - should_exit : True if the user wants to end the chat
    """
    cleaned = clean_input(user_input)

    # --- Step 1: empty input -------------------------------
    if cleaned == "":
        return EMPTY_INPUT_RESPONSE, False

    # --- Step 2: exit commands -----------------------------
    for phrase in EXIT_PHRASES:
        if matches_pattern(phrase, cleaned):
            return random.choice(FAREWELL_RESPONSES), True

    # --- Step 3: topic rules (first match wins) ------------
    for rule in RULES:
        for pattern in rule["patterns"]:
            if matches_pattern(pattern, cleaned):
                return random.choice(rule["responses"]), False

    # --- Step 4: nothing matched -> fallback ---------------
    return FALLBACK_RESPONSE, False

# =====================================================================
# 5. CONSOLE INTERFACE & MAIN LOOP
# =====================================================================

def print_bot_message(message):
    """Print a chatbot message; extra lines are indented neatly."""
    lines = message.split("\n")
    print(f"Chatbot: {lines[0]}")
    for line in lines[1:]:
        print(f"          {line}")


def chatbot():
    """Run the chatbot until the user types an exit command."""
    print("=" * 50)
    print("          RULE-BASED AI CHATBOT")
    print(f"          {ORGANIZATION}")
    print("=" * 50)
    print()
    print_bot_message(f"Hello! I am {BOT_NAME}, a Rule-Based AI Chatbot.")
    print_bot_message("Type 'help' to see what I can do.")
    print()

    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            # User pressed Ctrl+C or Ctrl+D - exit politely
            print()
            print_bot_message(random.choice(FAREWELL_RESPONSES))
            break

        response, should_exit = get_response(user_input)
        print_bot_message(response)
        print()

        if should_exit:
            break

    print("=" * 50)
    print("           Chatbot session ended.")
    print("=" * 50)


if __name__ == "__main__":
    chatbot()