import datetime
import platform
import random
import string
import subprocess
import urllib.parse
import webbrowser

import pyttsx3
import speech_recognition as sr

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

LISTEN_TIMEOUT = 5        # seconds to wait for the user to start speaking
PHRASE_TIME_LIMIT = 8     # maximum seconds for one spoken command
SPEECH_RATE = 170         # words per minute for spoken replies

# Phrases that end the session
EXIT_PHRASES = ["exit", "quit", "stop", "goodbye", "bye"]

# Words that count as a greeting
GREETING_WORDS = ["hello", "hi", "hey",
                  "good morning", "good afternoon", "good evening"]

# Websites the assistant can open (real, public URLs only)
WEBSITE_COMMANDS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
}

# Local applications the assistant may launch (Windows only).
# SECURITY: this whitelist is the ONLY way voice input can start a
# program - recognized text is never passed to a shell directly.
APP_COMMANDS = {
    "calculator": "calc.exe",
    "notepad": "notepad.exe",
}

# Predefined jokes - no external API needed
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the computer go to the doctor? Because it caught a virus!",
    "Why do Java developers wear glasses? Because they don't see sharp!",
    "Why did the developer go broke? Because he used up all his cache!",
    "I told my computer I needed a break, and it said: no problem, "
    "I'll go to sleep!",
]

INTRO_TEXT = ("I am a simple AI voice assistant built using Python, "
              "developed as part of the AI/ML internship at RaushByte "
              "Technologies. I can tell the time and date, open websites, "
              "search the web, open the calculator and notepad, and "
              "tell jokes. Say help to hear everything I can do.")

HELP_TEXT = ("You can ask me to: tell the current time, tell today's "
             "date, open Google, open YouTube, open GitHub, search the "
             "web, open the calculator, open notepad, tell a joke, or "
             "introduce myself. Say exit to stop me.")

# Table used to strip punctuation from recognized text
PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation)

# The text-to-speech engine is created once, when the program starts.
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty("rate", SPEECH_RATE)
except Exception as tts_error:
    print("Warning: text-to-speech could not be initialized -", tts_error)
    tts_engine = None   # the assistant still works with printed replies


# ------------------------------------------------------------------
# 1. Speaking (text-to-speech, fully offline)
# ------------------------------------------------------------------

def speak(text):
    """Print the assistant's reply, then speak it through the speakers."""
    print(f"Assistant: {text}")
    if tts_engine is not None:
        tts_engine.say(text)
        tts_engine.runAndWait()


# ------------------------------------------------------------------
# 2. Listening (microphone -> speech-to-text)
# ------------------------------------------------------------------

def listen(recognizer):
    """Capture speech from the microphone and convert it to text.

    Returns the recognized text, or None if nothing usable was heard.
    All three failure modes are handled with their own spoken message:
      - silence (timeout)
      - unintelligible speech (sr.UnknownValueError)
      - recognition service unreachable (sr.RequestError)
    """
    with sr.Microphone() as source:
        print("Listening...")
        # Calibrate to the room's background noise so detection
        # works in both quiet and noisy environments.
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(
                source,
                timeout=LISTEN_TIMEOUT,          # give up if user is silent
                phrase_time_limit=PHRASE_TIME_LIMIT,
            )
        except sr.WaitTimeoutError:
            return None                           # silence -> listen again

    try:
        # Google Web Speech API: free, no API key, needs internet.
        text = recognizer.recognize_google(audio)
        print(f"User: {text}")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand what you said.")
        return None
    except sr.RequestError:
        speak("Speech recognition service is currently unavailable.")
        return None


# ------------------------------------------------------------------
# 3. Text cleaning & matching helpers
# ------------------------------------------------------------------

def clean_command(command):
    """Lowercase, remove punctuation and extra spaces.

    Makes 'What's the time?' and 'what is the time' behave the same.
    """
    text = command.lower().strip().translate(PUNCTUATION_TABLE)
    return " ".join(text.split())


def contains_phrase(phrase, text):
    """Whole-word matching so 'hi' does NOT match inside 'this'.

    Both strings are padded with spaces, so only complete words or
    phrases can match. (Reused from my Level 1 chatbot task.)
    """
    return f" {phrase} " in f" {text} "


# ------------------------------------------------------------------
# 4. Task functions (one small job each)
# ------------------------------------------------------------------

def tell_time():
    """Speak the current time, read live from the system clock."""
    # lstrip("0") turns '07:30 PM' into '7:30 PM' for natural speech
    current_time = datetime.datetime.now().strftime("%I:%M %p").lstrip("0")
    speak(f"The current time is {current_time}.")


def tell_date():
    """Speak today's date, read live from the system clock."""
    today = datetime.datetime.now().strftime("%d %B %Y")
    speak(f"Today's date is {today}.")


def open_website(url, name):
    """Open a website in the default browser and confirm aloud."""
    webbrowser.open(url)
    speak(f"Opening {name}.")


def search_web(query):
    """Open Google search results for the query in the browser."""
    search_url = ("https://www.google.com/search?q="
                  + urllib.parse.quote_plus(query))
    webbrowser.open(search_url)
    speak(f"Searching for {query}.")


def open_application(app_name):
    """Launch a predefined local application (Windows only).

    SECURITY: 'app_name' is looked up in the APP_COMMANDS whitelist -
    it is never used as a raw command. Anything not whitelisted is
    refused before this function is even called.
    """
    if platform.system() != "Windows":
        speak("Sorry, opening applications is currently supported "
              "on Windows only.")
        return
    try:
        subprocess.Popen(APP_COMMANDS[app_name])
        speak(f"Opening {app_name}.")
    except FileNotFoundError:
        speak(f"Sorry, I couldn't find {app_name} on this computer.")


def tell_joke():
    """Speak one joke from the predefined list (no external API)."""
    speak(random.choice(JOKES))


# ------------------------------------------------------------------
# 5. Command processing (the assistant's "brain")
# ------------------------------------------------------------------

def process_command(command):
    """Match recognized text against predefined commands and run the task.

    Returns True to keep listening, or False when the user asked to exit.
    """
    text = clean_command(command)

    if not text:
        return True                     # nothing usable -> listen again

    # 1. Exit commands (checked first so they always work)
    if any(contains_phrase(word, text) for word in EXIT_PHRASES):
        speak("Goodbye! Have a great day.")
        return False

    # 2. Greetings
    if any(contains_phrase(word, text) for word in GREETING_WORDS):
        speak("Hello! How can I help you?")
        return True

    # 3. Help
    if (contains_phrase("help", text) or "what can you do" in text
            or contains_phrase("commands", text)):
        speak(HELP_TEXT)
        return True

    # 4. Introduction
    if ("who are you" in text or contains_phrase("your name", text)
            or "introduce yourself" in text):
        speak(INTRO_TEXT)
        return True

    # 5. "open ..." -> predefined application or website
    #    (checked before time/date so 'open youtube' is never
    #     mistaken for anything else)
    if text.startswith("open"):
        target = text[len("open"):].strip()
        if target.startswith("the "):          # "open the calculator"
            target = target[len("the "):].strip()
        if target in APP_COMMANDS:
            open_application(target)
        elif target in WEBSITE_COMMANDS:
            open_website(WEBSITE_COMMANDS[target], target.capitalize())
        else:
            speak("Sorry, I can only open Google, YouTube, GitHub, "
                  "the calculator, or notepad.")
        return True

    # 6. "search ..." / "search for ..."
    #    (before time/date so 'search for time management tips'
    #     is treated as a search, not a time question)
    if text.startswith("search"):
        query = text[len("search"):].strip()
        if query.startswith("for "):
            query = query[len("for "):].strip()
        if not query:
            speak("What would you like me to search for?")
        else:
            search_web(query)
        return True

    # 7. Jokes
    if contains_phrase("joke", text):
        tell_joke()
        return True

    # 8. Time and date
    if contains_phrase("time", text):
        tell_time()
        return True
    if contains_phrase("date", text):
        tell_date()
        return True

    # 9. Unknown command - graceful fallback, never a crash
    speak("Sorry, I didn't understand that command. "
          "Please try again or say help.")
    return True


# ------------------------------------------------------------------
# 6. Main application
# ------------------------------------------------------------------

def main():
    """Start the assistant, run the listening loop, and exit safely."""
    print("=" * 40)
    print("       AI VOICE ASSISTANT")
    print("       RaushByte Technologies")
    print("=" * 40)
    print("Press Ctrl+C to force stop.\n")

    # --- Microphone availability check (before anything else) ----
    try:
        with sr.Microphone():
            pass
    except (OSError, AttributeError, AssertionError) as error:
        print("Microphone could not be accessed.")
        print("Please check your microphone connection and permissions.")
        print("(Details:", error, ")")
        return

    recognizer = sr.Recognizer()
    speak("Hello! How can I help you?")

    # --- Conversation loop: listen -> process -> repeat ----------
    try:
        while True:
            command = listen(recognizer)
            if command is None:
                continue                 # nothing understood -> retry

            should_continue = process_command(command)
            if not should_continue:
                break                    # user said exit
    except KeyboardInterrupt:
        # Ctrl+C pressed - say goodbye instead of crashing
        print()
        speak("Goodbye! Have a great day.")

    print("=" * 40)
    print("     Voice assistant session ended.")
    print("=" * 40)


if __name__ == "__main__":
    main()