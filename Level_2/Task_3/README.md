# AI Desktop Automation Assistant using Python

**Automating Repetitive Computer Tasks with Python**

**Internship:** AI/ML Internship – RaushByte Technologies
**Task:** Level 2 – Task 3: AI Automation
**Prepared By:** Sandhiya

---

## Overview

This project is a **Python-based desktop automation assistant with rule-based natural-language command mapping**.

It runs in the terminal, accepts either a **menu number** or a **natural-language command** (e.g., *"take screenshot"* or *"capture screen"*), and safely automates common repetitive tasks such as:

* Opening websites and applications
* Creating folders
* Creating files and notes
* Taking screenshots
* Listing and renaming files
* Organizing files by extension
* Performing web searches
* Displaying system information

> ⚠️ **Honest Description:** This project uses Python automation and rule-based command mapping — **not machine learning**. No ML model is trained or used. See the *Natural-Language Command Mapping* section below.

---

## Objective

Repetitive computer tasks — creating the same folders, saving notes, tidying downloads, and taking screenshots — consume time and can lead to manual errors.

This assistant demonstrates how Python can automate such tasks **safely**.

Every action is predefined, whitelisted, and restricted to a dedicated workspace, ensuring that automation does not become a security risk.

---

## Features

* Website automation using `webbrowser`

  * Google
  * YouTube
  * GitHub
* Application launching using a **whitelist**

  * Calculator
  * Notepad
* Current time and date using the system clock
* Folder creation with name validation
* Text file creation with name validation
* Quick notes saved as timestamped `.txt` files
* Screenshot automation with timestamped filenames
* File listing from the workspace
* **File organizer**

  * Sorts files into:

    * Images
    * Documents
    * Excel
    * Python
    * Others
  * Provides a preview plan before moving files
  * Requires user confirmation
* Safe interactive file renaming
* Web search automation using the browser
* System information:

  * CPU
  * Memory
  * Disk
* Natural-language command mapping
* Menu numbers or natural-language commands
* Friendly error handling with no tracebacks or crashes on invalid input

---

## Technologies

| Technology             | Purpose                                                                    |
| ---------------------- | -------------------------------------------------------------------------- |
| **Python**             | Core programming language                                                  |
| **webbrowser**         | Website and search automation                                              |
| **pathlib / os**       | Safe file and folder operations                                            |
| **shutil**             | Moving files in the organizer; move-only, never delete                     |
| **subprocess**         | Launching whitelisted applications only                                    |
| **datetime**           | Time, date, and timestamped filenames                                      |
| **Pillow (ImageGrab)** | Screenshot capture; read-only screen access with no mouse/keyboard control |
| **psutil**             | CPU, memory, and disk information                                          |

> **Note:** `PyAutoGUI` is deliberately not used because this project does not require mouse or keyboard automation.

---

## Installation

From the `Task_3` folder in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If activation is blocked by PowerShell's execution policy, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This changes the execution policy for the **current user only** and does not require administrator rights.

Alternatively, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

---

## Run

After activating the virtual environment, run:

```powershell
python src/automation_assistant.py
```

The menu appears in the terminal.

You can enter:

* A menu number, such as `8`
* A natural-language command, such as `take screenshot`

To stop the assistant, type:

```text
exit
```

You can also press:

```text
Ctrl+C
```

---

## Example Commands

| You Type                                          | What Happens                                      |
| ------------------------------------------------- | ------------------------------------------------- |
| `open google` / `open browser` / `launch browser` | Opens Google                                      |
| `open calculator`                                 | Launches Windows Calculator                       |
| `what is the time`                                | Displays the current time                         |
| `what is today's date`                            | Displays today's date                             |
| `create folder project_files`                     | Creates a folder in the workspace                 |
| `create file notes.txt`                           | Creates an empty file in the workspace            |
| `create note` → then type the note                | Saves the note as `note_2026-...txt`              |
| `create note buy milk`                            | Saves `"buy milk"` directly as a note             |
| `take screenshot` / `capture screen`              | Saves a screenshot with a timestamp               |
| `list files`                                      | Displays a numbered list of workspace files       |
| `organize files`                                  | Sorts files by extension after confirmation       |
| `rename file`                                     | Starts an interactive, validated rename operation |
| `search python automation`                        | Opens Google search results                       |
| `system information`                              | Displays CPU, memory, and disk information        |
| `hello xyz abc`                                   | Displays a friendly fallback message              |
| `exit` / `quit` / `goodbye`                       | Closes the assistant                              |

---

## Project Workflow

```text
User Command
(menu number or natural language)
        ↓
Command Processing
(normalize text)
        ↓
Intent / Command Mapping
(rule-based phrase matching)
        ↓
Validation
(whitelists, filename checks, workspace restriction)
        ↓
Automation Function
(webbrowser / subprocess / pathlib / Pillow / psutil)
        ↓
Result
(confirmation or friendly error message)
        ↓
User
```

---

## Natural-Language Command Mapping

Different phrases are mapped to the same automation function using **predefined rules**.

This is **keyword/phrase matching**, not a machine-learning model.

| User Says                                                  | Mapped Action             |
| ---------------------------------------------------------- | ------------------------- |
| `take screenshot` / `capture screen` / `screenshot please` | `take_screenshot()`       |
| `open browser` / `launch browser` / `open google`          | `open_website("google")`  |
| `create note buy milk`                                     | `create_note("buy milk")` |
| `what is the time` / `what time is it` / `time please`     | `get_current_time()`      |

### How It Works

```text
User Input
    ↓
Normalize Text
    ↓
Check Predefined Phrases
    ↓
Match Known Command
    ↓
Validate Input
    ↓
Execute Safe Automation Function
    ↓
Display Result
```

---

## Safety

Arbitrary command execution is **structurally prevented** in this application.

### Security Measures

* **No `os.system(user_input)`**
* **No `subprocess` with `shell=True`**
* Applications can only be launched from the hardcoded `ALLOWED_APPLICATIONS` whitelist:

  * Calculator
  * Notepad
* Websites can only be opened from a fixed dictionary of approved URLs.
* All file and folder operations are restricted to:

```text
automation_workspace/
```

* Filename validation prevents:

  * Path separators
  * `..`
  * Unsafe file paths
* The file organizer:

  * Never deletes files
  * Never overwrites files
  * Shows a plan before moving files
  * Asks for confirmation
  * Renames duplicates such as `photo_1.jpg`
* Nothing runs secretly or in the background.
* Every action is visible in the terminal.

### Safe Automation Flow

```text
User Command
      ↓
Rule Matching
      ↓
Input Validation
      ↓
Whitelist Check
      ↓
Approved Automation
      ↓
Result Displayed to User
```

---

## Limitations

* Only understands predefined commands.
* Uses rule-based command mapping rather than conversational AI.
* Organizes only common file types.
* Unknown file extensions are moved to the `Others/` folder.
* Application launching depends on the application being installed on the computer.
* Screenshots capture the whole screen.
* No region-based screenshot selection is implemented.
* The application whitelist is primarily Windows-focused.
* macOS/Linux launch commands are included on a best-effort basis.

---

## Future Enhancements

The following features are **not implemented** in the current version:

* **Voice commands**

  * Integrate the Level 2 Task 2 Voice Assistant
* **AI-based intent classification**

  * Use an actual ML model for intent detection
* **GUI interface**
* **Scheduled automation**

  * Run tasks at predefined times
* **Task history logging**
* **More application integrations**
* **Offline AI model**

  * Use a local model for command understanding
* **Visual workflow builder**

---

## Author

**Sandhiya**

**AI/ML Intern – RaushByte Technologies**
