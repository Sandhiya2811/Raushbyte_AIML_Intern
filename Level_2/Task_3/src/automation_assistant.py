import datetime
import platform
import shutil
import subprocess
import urllib.parse
import webbrowser
from pathlib import Path

# ------------------------------------------------------------------
# Paths - anchored to this file, so there are NO hardcoded
# personal paths and the app works from any working directory.
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent      # Task_3 folder
WORKSPACE = BASE_DIR / "automation_workspace"          # all file operations
SCREENSHOT_DIR = BASE_DIR / "screenshots"              # screenshots saved here
SAMPLE_FOLDER = WORKSPACE / "sample_files"             # safe organizer test folder

# ------------------------------------------------------------------
# Whitelists - the safety core of the assistant
# ------------------------------------------------------------------

WEBSITE_COMMANDS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "browser": "https://www.google.com",   # "open browser" alias
}

# Only these two applications may ever be launched - and only via
# the exact commands listed here (never raw user text).
ALLOWED_APPLICATIONS = {
    "calculator": {
        "Windows": ["calc.exe"],
        "Darwin": ["open", "-a", "Calculator"],
        "Linux": ["gnome-calculator"],
    },
    "notepad": {
        "Windows": ["notepad.exe"],
        "Darwin": ["open", "-a", "TextEdit"],
        "Linux": ["gedit"],
    },
}

# Extension-based categories used by the file organizer
FILE_CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".ppt", ".pptx"},
    "Excel": {".xls", ".xlsx", ".csv"},
    "Python": {".py", ".ipynb"},
}
OTHERS_FOLDER = "Others"

# Characters that are never allowed inside a folder/file name
# (covers Windows rules; also blocks path separators and '..')
INVALID_FILENAME_CHARS = '<>:"/\\|?*'

# ------------------------------------------------------------------
# Natural-language command phrases (rule-based mapping, not ML)
# ------------------------------------------------------------------

EXIT_PHRASES = ["exit", "quit", "stop", "goodbye", "bye"]
HELP_PHRASES = ["help", "commands", "what can you do", "menu", "show menu"]
SCREENSHOT_PHRASES = ["take screenshot", "take a screenshot",
                      "capture screenshot", "capture screen",
                      "grab screenshot", "screenshot please", "screenshot"]
LIST_PHRASES = ["list files", "show files", "list all files", "show all files"]
ORGANIZE_PHRASES = ["organize files", "organize my files", "sort files",
                    "clean up files", "organize"]
RENAME_PHRASES = ["rename file", "rename a file", "rename"]
SYSTEM_INFO_PHRASES = ["system information", "system info", "system details",
                       "system status", "cpu usage", "memory usage",
                       "disk usage", "cpu", "memory", "disk"]

MENU_TITLE = """
==================================================
        AI DESKTOP AUTOMATION ASSISTANT
==================================================

Available Commands:

 1. Open Website        (open google / youtube / github)
 2. Open Application    (open calculator / notepad)
 3. Current Time        (what is the time)
 4. Current Date        (what is today's date)
 5. Create Folder       (create folder project_files)
 6. Create File         (create file notes.txt)
 7. Create Note         (create note)
 8. Take Screenshot     (take screenshot)
 9. List Files          (list files)
10. Organize Files      (organize files)
11. Rename File         (rename file)
12. Search Web          (search python automation)
13. System Information  (system information)
14. Help                (help)
15. Exit                (exit)

==================================================
"""


# ------------------------------------------------------------------
# Small helpers
# ------------------------------------------------------------------

def reply(message):
    """Print one assistant response line."""
    print(f"Assistant: {message}")


def clean_for_matching(text):
    """Punctuation-free copy of the command, used ONLY for matching
    phrases. (Arguments are extracted from the original text, so
    filenames like 'notes.txt' keep their dots.)"""
    text = text.replace("'", "")          # what's -> whats
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text)
    return " ".join(cleaned.split())


def contains_phrase(phrase, text):
    """Whole-word phrase matching: 'hi' will NOT match inside 'this'.
    (Reused from my Level 1 chatbot task.)"""
    return f" {phrase} " in f" {text} "


def is_valid_filename(name):
    """Return True only for a safe, single folder/file name."""
    name = name.strip()
    if not name or name in {".", ".."}:
        return False
    if any(ch in INVALID_FILENAME_CHARS for ch in name):
        return False
    if name.startswith(".") or name.endswith((".", " ")):
        return False
    if any(ord(ch) < 32 for ch in name):          # control characters
        return False
    return True


def safe_workspace_path(name):
    """Join 'name' to the workspace and verify the result stays
    inside it (defense in depth against path tricks)."""
    candidate = (WORKSPACE / name).resolve()
    if candidate.parent != WORKSPACE.resolve():
        return None
    return candidate


# ------------------------------------------------------------------
# Automation functions
# ------------------------------------------------------------------

def open_website(name):
    """Open a whitelisted website in the default browser."""
    url = WEBSITE_COMMANDS.get(name)
    if url is None:
        supported = ", ".join(k for k in WEBSITE_COMMANDS if k != "browser")
        reply(f"Sorry, I can only open: {supported}.")
        return
    webbrowser.open(url)
    reply(f"Opening {name}.")


def open_application(name):
    """Launch a whitelisted application. The launch command comes
    from ALLOWED_APPLICATIONS - never from raw user text."""
    app = ALLOWED_APPLICATIONS.get(name)
    if app is None:
        supported = ", ".join(ALLOWED_APPLICATIONS)
        reply(f"Sorry, I can only open these applications: {supported}.")
        return
    command = app.get(platform.system())
    if command is None:
        reply(f"Sorry, opening {name} is not supported on this operating system.")
        return
    try:
        subprocess.Popen(command)
        reply(f"Opening {name}.")
    except (FileNotFoundError, OSError):
        reply(f"Sorry, {name} could not be opened on this computer.")


def get_current_time():
    """Report the current time from the live system clock."""
    current = datetime.datetime.now().strftime("%I:%M %p").lstrip("0")
    reply(f"Current time: {current}")


def get_current_date():
    """Report today's date from the live system clock."""
    today = datetime.datetime.now().strftime("%d %B %Y")
    reply(f"Today's date: {today}")


def create_folder(folder_name):
    """Create a folder inside the automation workspace."""
    folder_name = folder_name.strip()
    if not is_valid_filename(folder_name):
        reply("Sorry, that is not a valid folder name. Use letters, numbers, "
              "spaces, dots, hyphens or underscores - no path separators.")
        return
    target = safe_workspace_path(folder_name)
    if target is None:
        reply("Sorry, that folder name is not allowed.")
        return
    try:
        target.mkdir()
        reply(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        reply("The folder already exists.")
    except OSError:
        reply("Sorry, the folder could not be created (permission problem).")


def create_file(file_name):
    """Create an empty text file inside the automation workspace."""
    file_name = file_name.strip()
    if not is_valid_filename(file_name):
        reply("Sorry, that is not a valid file name. Use letters, numbers, "
              "spaces, dots, hyphens or underscores - no path separators.")
        return
    target = safe_workspace_path(file_name)
    if target is None:
        reply("Sorry, that file name is not allowed.")
        return
    if target.exists():
        reply(f"A file named '{file_name}' already exists.")
        return
    try:
        target.touch()
        reply(f"File '{file_name}' created successfully in the workspace.")
    except OSError:
        reply("Sorry, the file could not be created.")


def create_note(content=None):
    """Save a short note as a timestamped .txt file in the workspace."""
    if content is None or content.strip() == "":
        content = input("Enter your note: ").strip()
    if not content:
        reply("The note was empty, so nothing was saved.")
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    target = WORKSPACE / f"note_{timestamp}.txt"
    try:
        target.write_text(content + "\n", encoding="utf-8")
        reply(f"Note saved as {target.name} in the workspace.")
    except OSError:
        reply("Sorry, the note could not be saved.")


def take_screenshot():
    """Capture the screen with Pillow's ImageGrab and save it with a
    timestamped filename. (ImageGrab only READS the screen - it has
    no mouse/keyboard control, which is why PyAutoGUI was not used.)"""
    try:
        from PIL import ImageGrab
    except ImportError:
        reply("Pillow is not installed. Install it with: python -m pip install Pillow")
        return
    try:
        SCREENSHOT_DIR.mkdir(exist_ok=True)
        image = ImageGrab.grab()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        path = SCREENSHOT_DIR / f"screenshot_{timestamp}.png"
        image.save(path)
        reply(f"Screenshot saved successfully as {path.name}.")
    except Exception:
        reply("Sorry, taking the screenshot failed on this system.")


def list_files():
    """List the files currently in the automation workspace."""
    try:
        files = sorted(f for f in WORKSPACE.iterdir() if f.is_file())
    except OSError:
        reply("Sorry, the workspace folder could not be read.")
        return
    if not files:
        reply("No files found in the automation workspace yet.")
        return
    print("Assistant: Files found:\n")
    for index, file_path in enumerate(files, start=1):
        print(f"  {index}. {file_path.name}")
    print()


def get_category(file_path):
    """Return the category folder name for a file, based on extension."""
    extension = file_path.suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    return OTHERS_FOLDER


def create_sample_files():
    """Create a small set of dummy files (text content, harmless)
    so the organizer can be tested safely without touching real data."""
    SAMPLE_FOLDER.mkdir(parents=True, exist_ok=True)
    sample_names = ["photo.jpg", "wallpaper.png", "resume.pdf", "notes.txt",
                    "data.csv", "script.py", "document.docx"]
    for name in sample_names:
        (SAMPLE_FOLDER / name).write_text(
            "Sample file created for testing the organizer.\n", encoding="utf-8")
    reply(f"Sample folder '{SAMPLE_FOLDER.name}' created with "
          f"{len(sample_names)} test files.")


def organize_files():
    """Organize the files of a chosen folder into category subfolders.
    Safety rules: never deletes, never overwrites, always asks for
    confirmation, and shows every move it makes."""
    raw = input("Press Enter to organize the sample folder, or type a folder path: "
                ).strip().strip('"')

    if raw == "":
        # Default: the dedicated sample folder inside the workspace
        target = SAMPLE_FOLDER
        if not target.exists():
            reply("The sample folder does not exist yet.")
            choice = input("Create it with a few dummy test files? (y/n): "
                           ).strip().lower()
            if choice.startswith("y"):
                create_sample_files()
            else:
                reply("Okay, nothing was organized.")
                return
    else:
        # A real folder chosen by the user - extra confirmation required
        target = Path(raw).expanduser()
        if not target.is_dir():
            reply("Sorry, that folder does not exist or is not a valid folder.")
            return
        confirm_real = input(
            f"Organize the real folder '{target}'? Files will only be MOVED, "
            f"never deleted. (y/n): ").strip().lower()
        if not confirm_real.startswith("y"):
            reply("Cancelled. No files were moved.")
            return

    # Build and show the plan BEFORE moving anything
    try:
        files = sorted(f for f in target.iterdir() if f.is_file())
    except OSError:
        reply("Sorry, that folder could not be read.")
        return
    if not files:
        reply("No files found to organize in that folder.")
        return

    plan = [(file_path, get_category(file_path)) for file_path in files]
    print(f"\nAssistant: {len(plan)} file(s) will be moved:\n")
    for file_path, category in plan:
        print(f"  {file_path.name}  ->  {category}/")
    print()

    choice = input(f"Move {len(plan)} file(s)? (y/n): ").strip().lower()
    if not choice.startswith("y"):
        reply("Cancelled. No files were moved.")
        return

    moved = 0
    for file_path, category in plan:
        destination_dir = target / category
        destination_dir.mkdir(exist_ok=True)
        destination = destination_dir / file_path.name
        duplicate_note = ""
        if destination.exists():
            # Never overwrite: pick photo_1.jpg, photo_2.jpg, ...
            counter = 1
            while (destination_dir / f"{file_path.stem}_{counter}{file_path.suffix}").exists():
                counter += 1
            destination = destination_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
            duplicate_note = f"  (saved as {destination.name} - name already existed)"
        try:
            shutil.move(str(file_path), str(destination))
            print(f"  Moved: {file_path.name} -> {category}/{destination.name}{duplicate_note}")
            moved += 1
        except (OSError, shutil.Error) as error:
            print(f"  Could not move {file_path.name}: {error}")

    reply(f"Done. {moved} of {len(plan)} file(s) organized into category folders.")


def rename_file():
    """Safely rename a file inside the workspace (interactive flow)."""
    try:
        files = sorted(f for f in WORKSPACE.iterdir() if f.is_file())
    except OSError:
        reply("Sorry, the workspace could not be read.")
        return
    if not files:
        reply("There are no files in the workspace to rename.")
        return

    print("Assistant: Files in the workspace:\n")
    for index, file_path in enumerate(files, start=1):
        print(f"  {index}. {file_path.name}")
    print()

    choice = input("Enter the number of the file to rename: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
        reply("Sorry, that is not a valid file number.")
        return
    file_to_rename = files[int(choice) - 1]

    new_name = input("Enter the new name (e.g., report.txt): ").strip()
    if not is_valid_filename(new_name):
        reply("Sorry, that is not a valid file name.")
        return
    new_path = safe_workspace_path(new_name)
    if new_path is None:
        reply("Sorry, that name is not allowed.")
        return
    if new_path.exists():
        reply("A file with that name already exists, so nothing was renamed.")
        return

    try:
        file_to_rename.rename(new_path)
        reply(f"File renamed successfully: {file_to_rename.name} -> {new_name}")
    except OSError:
        reply("Sorry, the file could not be renamed.")


def search_web(query):
    """Open Google search results for the query in the browser."""
    if not query:
        query = input("What would you like to search for? ").strip()
        if not query:
            reply("No search query given, so nothing was opened.")
            return
    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    webbrowser.open(url)
    reply(f"Searching for {query}.")


def get_system_info():
    """Show simple, read-only system information using psutil."""
    try:
        import psutil
    except ImportError:
        reply("psutil is not installed. Install it with: python -m pip install psutil")
        return
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(Path.cwd().anchor or "/")
    print("Assistant: System information:\n")
    print(f"  CPU Usage:        {cpu_percent}%")
    print(f"  Memory Usage:     {memory.percent}%")
    print(f"  Available Memory: {memory.available / (1024 ** 3):.1f} GB")
    print(f"  Disk Usage:       {disk.percent}%")
    print(f"  Free Disk Space:  {disk.free / (1024 ** 3):.1f} GB")
    print()


def print_help():
    """Show the menu and example natural commands."""
    print(MENU_TITLE)
    print("You can type a menu number (e.g., 8) or a natural command.")
    print("Examples: 'take screenshot', 'capture screen', 'open youtube',")
    print("'create folder project_files', 'create note buy milk', 'exit'.\n")


# ------------------------------------------------------------------
# Menu-number actions (for options 1-14; exit is handled directly)
# ------------------------------------------------------------------

def menu_open_website():
    name = input("Which website? (google / youtube / github): ").strip().lower()
    open_website(name)


def menu_open_application():
    name = input("Which application? (calculator / notepad): ").strip().lower()
    open_application(name)


def menu_create_folder():
    create_folder(input("Enter the folder name: ").strip())


def menu_create_file():
    create_file(input("Enter the file name (e.g., notes.txt): ").strip())


def menu_search_web():
    search_web(input("Enter your search query: ").strip())


MENU_ACTIONS = {
    "1": menu_open_website,
    "2": menu_open_application,
    "3": get_current_time,
    "4": get_current_date,
    "5": menu_create_folder,
    "6": menu_create_file,
    "7": create_note,
    "8": take_screenshot,
    "9": list_files,
    "10": organize_files,
    "11": rename_file,
    "12": menu_search_web,
    "13": get_system_info,
    "14": print_help,
}


# ------------------------------------------------------------------
# Command processing (rule-based natural-language mapping)
# ------------------------------------------------------------------

def process_command(command):
    """Interpret a user command (menu number or natural language)
    and run the matching automation. Returns False only to exit."""
    text = " ".join(command.lower().strip().split())
    if not text:
        reply("Please enter a command. Type 'help' to see available commands.")
        return True

    # Punctuation-free copy used ONLY for phrase matching
    match_text = clean_for_matching(text)

    # --- Menu numbers -------------------------------------------
    number = text.rstrip(".")
    if number == "15":
        reply("Goodbye! The automation assistant is now closed.")
        return False
    if number in MENU_ACTIONS:
        MENU_ACTIONS[number]()
        return True

    # --- 1. Exit (checked first so it always works) --------------
    if any(contains_phrase(phrase, match_text) for phrase in EXIT_PHRASES):
        reply("Goodbye! The automation assistant is now closed.")
        return False

    # --- 2. Help -------------------------------------------------
    if any(contains_phrase(phrase, match_text) for phrase in HELP_PHRASES):
        print_help()
        return True

    # --- 3. Screenshot (multiple natural phrasings) ---------------
    if any(contains_phrase(phrase, match_text) for phrase in SCREENSHOT_PHRASES):
        take_screenshot()
        return True

    # --- 4-6. Create folder / file / note (prefix + argument) -----
    for prefix in ("create folder", "make folder", "new folder"):
        if text.startswith(prefix):
            create_folder(text[len(prefix):].strip())
            return True
    for prefix in ("create file", "make file", "new file"):
        if text.startswith(prefix):
            create_file(text[len(prefix):].strip())
            return True
    for prefix in ("create note", "make a note", "new note", "take a note"):
        if text.startswith(prefix):
            create_note(text[len(prefix):].strip())
            return True

    # --- 7-9. Rename / organize / list -----------------------------
    if any(contains_phrase(phrase, match_text) for phrase in RENAME_PHRASES):
        rename_file()
        return True
    if any(contains_phrase(phrase, match_text) for phrase in ORGANIZE_PHRASES):
        organize_files()
        return True
    if any(contains_phrase(phrase, match_text) for phrase in LIST_PHRASES):
        list_files()
        return True

    # --- 10. Web search ("search for" before "search"!) ------------
    for prefix in ("search for", "search", "google"):
        if text.startswith(prefix):
            search_web(text[len(prefix):].strip())
            return True

    # --- 11. Open website / application (whitelists only) ----------
    for prefix in ("open", "launch"):
        if text.startswith(prefix):
            target = text[len(prefix):].strip()
            if target.startswith("the "):        # "open the calculator"
                target = target[len("the "):].strip()
            if target in ALLOWED_APPLICATIONS:
                open_application(target)
            else:
                open_website(target)             # replies with the
            return True                          # supported list if unknown

    # --- 12. System information ------------------------------------
    if any(contains_phrase(phrase, match_text) for phrase in SYSTEM_INFO_PHRASES):
        get_system_info()
        return True

    # --- 13. Time and date ------------------------------------------
    if contains_phrase("time", match_text):
        get_current_time()
        return True
    if contains_phrase("date", match_text):
        get_current_date()
        return True

    # --- 14. Simple greeting (exact match only, so that
    #        "hello xyz abc" correctly falls through to the fallback) -
    if match_text in ("hello", "hi", "hey"):
        reply("Hello! Type 'help' to see everything I can automate.")
        return True

    # --- 15. Unknown command -----------------------------------------
    reply("Sorry, I didn't understand that command. "
          "Type 'help' to see available commands.")
    return True


# ------------------------------------------------------------------
# Main application
# ------------------------------------------------------------------

def main():
    """Start the automation assistant and run the command loop."""
    try:
        WORKSPACE.mkdir(exist_ok=True)
        SCREENSHOT_DIR.mkdir(exist_ok=True)
    except OSError:
        print("Error: could not create the automation workspace folder.")
        return

    print(MENU_TITLE)
    reply("Hello! I am your AI Desktop Automation Assistant.")
    reply("Type a menu number or a natural command (e.g., 'take screenshot').")

    while True:
        try:
            command = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print()
            reply("Goodbye! The automation assistant is now closed.")
            break

        try:
            if not process_command(command):
                break
        except Exception as error:
            # Friendly message instead of a raw traceback (task section 20)
            reply(f"Sorry, something went wrong while running that command "
                  f"({type(error).__name__}). Type 'help' to see available commands.")


if __name__ == "__main__":
    main()