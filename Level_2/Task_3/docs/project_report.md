# Project Report — AI Desktop Automation Assistant using Python

**Internship:** AI/ML Internship
**Organization:** RaushByte Technologies
**Task:** Level 2 – Task 3: AI Automation
**Prepared By:** Sandhiya

---

## 1. Introduction

**Computer automation** means using software to perform tasks that a person would otherwise do manually — opening the same applications, creating the same folder structures, saving notes, tidying downloaded files, and capturing screenshots.

These **repetitive tasks** are small individually but add up to significant time. Because they are repetitive, they can also lead to manual errors.

A **desktop automation assistant** is a program that accepts simple commands and performs such tasks on the user's behalf — quickly, consistently, and, if designed correctly, safely.

---

## 2. Problem Statement

Repetitive computer tasks consume time and can cause manual errors. A solution is needed that can:

* Perform common tasks such as:

  * File and folder operations
  * Note creation
  * Screenshots
  * Website opening
  * Web search
  * File organization
* Accept natural phrasing so users do not have to memorize exact syntax
* Be **safe by design**

  * Never execute arbitrary user input as system commands
  * Never delete or overwrite files
  * Restrict file operations to a dedicated workspace
* Handle invalid input gracefully instead of crashing
* Run on a standard computer using free libraries only

---

## 3. Objective

Build a Python-based desktop automation assistant that:

* Accepts both **menu numbers** and **natural-language commands**
* Maps multiple phrasings of the same request to one automation function
* Uses rule-based command mapping, honestly distinguished from machine learning
* Automates:

  * Websites
  * Applications
  * Time and date
  * Folders
  * Files
  * Notes
  * Screenshots
  * File listing
  * File organization by extension
  * File renaming
  * Web search
  * System information
* Enforces safety through:

  * Whitelists
  * Input validation
  * Workspace restriction
  * Confirmation prompts
  * No-overwrite rules
  * No-delete rules
* Exits cleanly
* Handles common errors with friendly messages

---

## 4. Technologies Used

| Technology                | Purpose                                                                                                                              |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Python 3**              | Core programming language                                                                                                            |
| **webbrowser** (stdlib)   | Opens websites and search results in the default browser                                                                             |
| **pathlib** (stdlib)      | Object-oriented, cross-platform file/folder handling; all paths are anchored to the script location with no hardcoded personal paths |
| **shutil** (stdlib)       | Moves files in the organizer; move-only and never deletes                                                                            |
| **subprocess** (stdlib)   | Launches the two whitelisted applications; commands are passed as lists and never through a shell                                    |
| **datetime** (stdlib)     | Provides time/date responses and timestamped filenames                                                                               |
| **urllib.parse** (stdlib) | Safely encodes web-search queries into URLs                                                                                          |
| **platform** (stdlib)     | Chooses the correct whitelisted application launch command based on the operating system                                             |
| **Pillow**                | Screenshot capture using `ImageGrab`; reads the screen only                                                                          |
| **psutil**                | Provides CPU, memory, and disk usage information                                                                                     |

> **Note:** PyAutoGUI was deliberately not used because mouse and keyboard control are unnecessary for this project and would expand the security risk surface.

---

## 5. System Architecture

```text
User Command
(menu number or natural language)
        ↓
Command Processing
(normalize text: lowercase, collapse spaces)
        ↓
Intent / Command Mapping
(rule-based phrase matching)
        ↓
Validation
(application/website whitelists,
filename rules,
workspace restriction via resolved-path check)
        ↓
Automation Function
(webbrowser / subprocess / pathlib /
shutil / Pillow / psutil / datetime)
        ↓
Result
(confirmation message or friendly error)
        ↓
User
        ↓
Loop continues until "exit"
```

---

## 6. Automation Features

| Feature                | What It Does                                                   | Validation / Safety                                                                |
| ---------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Open website**       | Opens Google, YouTube, or GitHub using `webbrowser`            | Fixed URL dictionary; no user-supplied URLs                                        |
| **Open application**   | Launches Calculator or Notepad                                 | `ALLOWED_APPLICATIONS` whitelist; `subprocess.Popen` with a command list; no shell |
| **Time / date**        | Displays live values from `datetime.now()`                     | Nothing is hardcoded                                                               |
| **Create folder**      | Creates a folder inside the workspace                          | Name validation; `FileExistsError` handled; resolved-path check                    |
| **Create file**        | Creates an empty file inside the workspace                     | Same validation; refuses if the file already exists                                |
| **Create note**        | Saves a note as `note_<timestamp>.txt`                         | Content can be provided through the command or prompt                              |
| **Screenshot**         | Uses `ImageGrab.grab()` and saves `screenshot_<timestamp>.png` | Saves inside `screenshots/`; failures are handled                                  |
| **List files**         | Displays a numbered list of workspace files                    | Read-only                                                                          |
| **Organize files**     | Moves files into category folders                              | Plan preview + confirmation; no deletion; no overwriting; duplicate renaming       |
| **Rename file**        | Provides an interactive rename operation                       | Number selection; name validation; refuses existing targets                        |
| **Web search**         | Opens an encoded Google search URL                             | Uses `urllib.parse.quote_plus`; no scraping                                        |
| **System information** | Displays CPU, memory, and disk information using `psutil`      | Read-only statistics                                                               |

---

### Natural-Language Command Mapping

Multiple phrasings map to the same function through predefined rules.

For example:

* *"take screenshot"*
* *"capture screen"*
* *"screenshot please"*

All trigger:

```python
take_screenshot()
```

Prefix commands can also extract arguments:

```text
create folder project_files
        ↓
create_folder("project_files")
```

Another example:

```text
create note buy milk
        ↓
create_note("buy milk")
```

This saves the note content directly without requiring an additional prompt.

### Honest Scope

This project uses **rule-based matching**, including:

* Phrase lists
* Whole-word comparison
* Prefix extraction

It is **not machine learning**.

No model is trained, and no learning happens at runtime.

> If an ML-based intent classifier is added in the future, it should be described as a separate AI component.

---

## 7. File Organization Method

The file organizer sorts files according to their extensions into category subfolders.

| Category      | Extensions                                               |
| ------------- | -------------------------------------------------------- |
| **Images**    | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg` |
| **Documents** | `.pdf`, `.doc`, `.docx`, `.txt`, `.md`, `.ppt`, `.pptx`  |
| **Excel**     | `.xls`, `.xlsx`, `.csv`                                  |
| **Python**    | `.py`, `.ipynb`                                          |
| **Others**    | Any other extension                                      |

### Organization Procedure

```text
Choose Folder
    ↓
Enter = Safe sample_files Folder
    ↓
Custom Folder?
    ↓
Extra Confirmation Required
    ↓
Scan Top-Level Files Only
    ↓
Build Move Plan
    ↓
Display Move Plan
    ↓
Ask User for y/n Confirmation
    ↓
Move Files Using shutil.move()
    ↓
Print Every Move
```

If a destination filename already exists, the incoming file is automatically renamed:

```text
photo.jpg
photo_1.jpg
photo_2.jpg
photo_3.jpg
```

Therefore:

> **Nothing is ever deleted or overwritten.**

If the sample folder is missing, the assistant can create it with dummy test files. This allows testing without touching real user data.

---

## 8. Safety Mechanisms

### 1. Whitelisted Commands Only

Applications and websites come from hardcoded dictionaries.

Anything outside the supported list is refused with a friendly message.

---

### 2. No Arbitrary Shell Execution

`os.system()` is never used.

`subprocess` is called only with predefined command lists:

* No `shell=True`
* No user-provided shell commands
* No arbitrary system command execution

---

### 3. Workspace Restriction

Create and rename operations are restricted to:

```text
automation_workspace/
```

Filenames are validated to prevent:

* Path separators
* `..`
* Invalid characters

The resolved path is also re-checked to ensure it remains inside the workspace.

---

### 4. Confirmation Before Moving Real Files

The organizer:

1. Shows the complete move plan.
2. Requires `y/n` confirmation.
3. Requires an additional confirmation for real, non-sample folders.

---

### 5. No Deletion and No Overwriting

The organizer only moves files.

If a destination filename already exists, the program automatically creates a unique filename.

Example:

```text
report.pdf
report_1.pdf
report_2.pdf
```

---

### 6. Full Visibility

Every operation is printed in the terminal.

Nothing runs:

* Hidden
* Silently
* In the background

---

## 9. Implementation

The program is organized into small, single-purpose functions.

### Main Components

| Component               | Responsibility                                  |
| ----------------------- | ----------------------------------------------- |
| `reply()`               | Displays responses to the user                  |
| `clean_for_matching()`  | Normalizes command text                         |
| `contains_phrase()`     | Performs phrase matching                        |
| `is_valid_filename()`   | Validates filenames                             |
| `safe_workspace_path()` | Ensures paths remain inside the workspace       |
| Automation functions    | Perform individual tasks                        |
| `menu_*()` functions    | Handle interactive menu options                 |
| `process_command()`     | Acts as the rule-based command-processing brain |
| `main()`                | Handles startup and the main interaction loop   |

The `contains_phrase()` helper uses the phrase-padding technique reused from the Level 1 chatbot to avoid incorrect partial matches.

Paths are anchored with:

```python
Path(__file__).resolve().parent.parent
```

Therefore, there are no hardcoded personal paths, and the application can work from different working directories.

The main loop also wraps command processing in a broad exception handler so users receive a friendly error message instead of a traceback.

Expected errors such as:

* Missing folders
* Permission problems
* Missing applications

are handled specifically inside the relevant functions.

---

## 10. Testing

> **Testing Requirement:** Run each test yourself and record the actual result. The **Status** column is intentionally left blank so that no test is marked as passed before execution.

| Test Case                     | Input                                | Expected Result                                | Status   |
| ----------------------------- | ------------------------------------ | ---------------------------------------------- | -------- |
| Open website                  | `open google`                        | Browser opens Google                           | *(fill)* |
| Open application              | `open calculator`                    | Calculator launches                            | *(fill)* |
| Current time                  | `what is the time`                   | Correct time displayed                         | *(fill)* |
| Current date                  | `what is today's date`               | Correct date displayed                         | *(fill)* |
| Create folder                 | `create folder test`                 | Folder created message                         | *(fill)* |
| Create file                   | `create file notes.txt`              | File created message                           | *(fill)* |
| Duplicate folder              | `create folder test` again           | `"The folder already exists."`                 | *(fill)* |
| Screenshot                    | `take screenshot`                    | `"Screenshot saved successfully as …"`         | *(fill)* |
| List files                    | `list files`                         | Numbered file list                             | *(fill)* |
| Organize files                | `organize files` using sample folder | Files moved into Images/Documents/Excel/Python | *(fill)* |
| Rename file                   | `rename file`                        | File renamed confirmation                      | *(fill)* |
| Web search                    | `search python automation`           | Google results open                            | *(fill)* |
| System information            | `system information`                 | CPU/memory/disk information shown              | *(fill)* |
| Invalid command               | `hello xyz abc`                      | Friendly fallback message                      | *(fill)* |
| Empty input                   | Press `Enter`                        | `"Please enter a command."`                    | *(fill)* |
| Security: non-whitelisted app | `open cmd`                           | Refused; supported list shown                  | *(fill)* |
| Exit                          | `exit`                               | Assistant closes cleanly                       | *(fill)* |

---

## 11. Results

After running the test suite, the assistant performs the supported automations through both menu numbers and natural-language commands.

The expected functionality includes:

* Opening websites and applications
* Reporting live time and date
* Creating folders, files, and notes inside the workspace
* Saving timestamped screenshots
* Listing and renaming files safely
* Organizing the sample folder into category folders
* Displaying a move plan and requesting confirmation
* Opening web-search results
* Displaying system statistics
* Handling invalid and empty input with friendly messages
* Rejecting non-whitelisted applications
* Exiting cleanly

The application is designed to avoid crashes or tracebacks during normal use, and arbitrary system commands cannot be executed through the assistant.

> **Update this section with your actual observed results and screenshots after testing.**

---

## 12. Limitations

* Rule-based understanding only; unsupported phrasings receive the fallback response.
* The organizer handles common file extensions; unknown types are placed in `Others/`.
* The application whitelist is intentionally small:

  * Two applications
  * Three websites
* Screenshots capture the full screen only.
* Application launching depends on the target application being installed.
* No scheduling functionality is currently implemented.
* No GUI is currently implemented.
* No task history is currently implemented.

---

## 13. Privacy and Security

* **No hidden/background activity:** The assistant runs only while the terminal window is open and prints every action it performs.
* **Microphone/camera-free:** The assistant does not use a microphone or camera. Screenshots capture the screen only when explicitly commanded and are saved locally.
* **Data stays local:** Notes and files remain inside the project workspace. Nothing is uploaded.
* **Network activity:** The only network-related actions are opening websites or search results in the browser.
* **Unauthorized actions are structurally blocked:** There is no arbitrary shell execution, no writing outside the workspace, and no file deletion.
* **Transparency:** The organizer announces every move and asks for confirmation before processing real folders.

---

## 14. Future Enhancements

### Voice Control

Connect the Level 2 Task 2 **AI Voice Assistant** as the input layer.

### AI-Based Intent Classification

Replace the rule-based command table with a genuine ML model, such as a small text-classification model.

This would introduce a clearly identifiable AI component.

### GUI

Develop a graphical interface using:

* Tkinter
* Streamlit

### Scheduled Automation

Allow users to schedule tasks at predefined times.

### Task History

Maintain a log of completed automation tasks.

### More Integrations

Potential integrations include:

* Email drafts
* File backup
* Report generation

### Offline AI Model

Use a local AI model for more flexible command understanding.

### Visual Workflow Builder

Allow users to visually chain multiple automation tasks together.

---

## 15. Conclusion

This project delivered a working, **safety-first desktop automation assistant**.

Beyond the automation itself, the project provided practical learning in **secure software design**. Arbitrary command execution is prevented through application and website whitelists, filename validation, workspace restrictions, confirmation prompts, and a move-only file organizer.

The project also demonstrated how to design automation systems with **data safety in mind**. The organizer never deletes or overwrites files, automatically handles duplicate filenames, and asks for confirmation before moving files.

Most importantly, the project taught me to describe AI systems accurately. The assistant's command-understanding layer uses **rule-based phrase matching**, not machine learning. No ML model is trained and no learning occurs at runtime.

This distinction helps maintain technical accuracy while providing a strong foundation for future enhancements such as ML-based intent classification, voice control, GUI integration, and offline AI-powered command understanding.
