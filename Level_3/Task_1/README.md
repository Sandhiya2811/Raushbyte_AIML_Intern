# Smart AI Assistant using Python and LLM

**An Intelligent Conversational Assistant for Question Answering and Basic Task Automation**

**Internship:** AI/ML Internship – RaushByte Technologies
**Task:** Level 3 – Task 1: Smart AI Assistant
**Prepared By:** Sandhiya

---

## Overview

This project is an **LLM-powered conversational assistant with safe Python-based task tools**.

It answers general questions using a **locally installed Ollama model**, remembers recent conversation context for follow-up questions, and performs a small set of **predefined, safety-restricted tasks**, including:

* Date and time
* Approved websites
* Browser search
* Notes

> **Accurate Description — No Exaggeration:** This is an LLM + Python tools assistant. It does **not** implement RAG, agents, autonomous AI, web browsing, or real-time knowledge.
>
> The **web search** tool only *opens a search page in the browser*. It does not retrieve or read search results.

---

## Objective

Most assistants either **only chat** or **only run commands**. This project demonstrates both capabilities while keeping them cleanly separated.

### Question Answering

Handled by the **local LLM** with short-term conversation memory.

### Task Execution

Handled by a **deterministic, whitelisted Python tool layer**.

This separation keeps task execution structurally safe:

* The LLM can never directly trigger an action.
* User text is never executed as a system command.
* LLM-generated text is never executed as a system command.

---

## Features

* AI question answering using a **local Ollama LLM**
* No paid APIs or cloud LLM services required
* **Short-term conversation memory**

  * Supports follow-up questions such as:

    * `"Give me a simple example"`
* Current time and date using real system values
* Opening **approved websites only**

  * Google
  * YouTube
  * GitHub
  * LinkedIn
* Web search

  * Opens the browser
  * Does not scrape or retrieve search results
* Notes functionality:

  * Create notes
  * Read notes
  * List notes
* Notes are stored only inside `data/notes/`
* Rule-based natural-language command mapping
* Multiple phrasings can map to the same tool
* Safe tool execution using:

  * Whitelists
  * Path restrictions
  * Input validation
* Graceful error handling:

  * Ollama unavailable
  * Model missing
  * Invalid input
* Console interface
* Optional Streamlit web interface

---

## Architecture

```text
                         USER
                           │
                           ▼
                ┌─────────────────────┐
                │    Chat Interface   │
                │                     │
                │ Console: assistant.py
                │ Web: app.py         │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Intent Detection  │
                │ Rule-based and      │
                │ deterministic       │
                └──────────┬──────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
      ┌────────────────┐        ┌─────────────────┐
      │ General        │        │ Basic Task      │
      │ Question       │        │                 │
      └───────┬────────┘        └────────┬────────┘
              │                          │
              ▼                          ▼
      ┌────────────────┐        ┌─────────────────┐
      │ Local LLM      │        │ Tool Layer      │
      │ Ollama         │        │ tools.py        │
      │ + Memory       │        └────────┬────────┘
      └───────┬────────┘                 │
              │                ┌─────────┼─────────┐
              │                ▼         ▼         ▼
              │              Time/    Browser    Notes
              │              Date     Whitelist  Jailed
              │
              └──────────────┬───────────────┐
                             ▼               │
                    ┌─────────────────┐      │
                    │ Final Response  │◄─────┘
                    │ Tool results    │
                    │ shown verbatim  │
                    └────────┬────────┘
                             │
                             ▼
                            USER
```

---

## Technologies

| Technology                    | Purpose                                                       |
| ----------------------------- | ------------------------------------------------------------- |
| **Python 3**                  | Core application                                              |
| **Ollama (`ollama` package)** | Local LLM inference for question answering                    |
| **Prompt Engineering**        | Defines assistant personality, honesty rules, and limitations |
| **`datetime`**                | Provides real date and time values                            |
| **`webbrowser`**              | Opens approved websites and search pages                      |
| **`pathlib`**                 | Provides safe and validated file handling for notes           |
| **python-dotenv**             | Loads configuration from `.env`                               |
| **Streamlit**                 | Optional web interface                                        |

---

## Requirements

### Python

* **Python 3.8+**

### Ollama

Ollama must be installed on the computer.

Download Ollama from:

[Ollama Download](https://ollama.com/download?utm_source=chatgpt.com)

### Pull an LLM Model

For example:

```powershell
ollama pull llama3.2:3b
```

Check installed models using:

```powershell
ollama list
```

You can also use another compatible model, such as:

* `mistral`
* `qwen2.5:3b`

The model name is configurable and is not hardcoded.

Set the model name in `.env`:

```text
OLLAMA_MODEL=your-model-name
```

### Start Ollama

Ollama must be running before starting the assistant.

On Windows/macOS, the Ollama application can run in the system tray.

Alternatively, start the Ollama server using:

```powershell
ollama serve
```

---

## Installation

From the `Task_1` folder in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

After copying `.env.example`, edit `.env` if you need to change the model name.

### PowerShell Execution Policy

If virtual-environment activation is blocked by PowerShell's execution policy, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This applies to the **current user only** and does not require administrator rights.

Alternatively, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

---

## Run

### Console Version

Run:

```powershell
python src/assistant.py
```

### Streamlit Web Version

The Streamlit interface is optional.

Run:

```powershell
streamlit run src/app.py
```

---

## Example Conversation

> **Note:** LLM responses can vary depending on the selected model. The following conversation is representative.

```text
You: What is machine learning?

Assistant: Machine learning is a branch of AI where computers learn
patterns from data instead of being programmed with fixed rules.

You: Give me a simple example.

Assistant: A classic example is email spam detection — the system studies
thousands of emails labelled spam/not-spam and learns to classify new ones.

You: What time is it?

Assistant: The current time is 10:32 AM.

You: Open GitHub.

Assistant: Opening GitHub in your browser.

You: Create a note called interview.txt with:
Revise Python, SQL and machine learning.

Assistant: I've saved your note as 'interview.txt'.
Content: Revise Python, SQL and machine learning.

You: Read interview.txt.

Assistant: Here is your note 'interview.txt':

Revise Python, SQL and machine learning.

You: open cmd

Assistant: Sorry, 'cmd' is not an approved website.
I can only open: google, youtube, github, linkedin.

You: exit

Assistant: Goodbye! Have a great day.
```

---

## Safety

The assistant follows a **deterministic and restricted tool architecture**.

### 1. The LLM Never Executes Anything

The LLM only produces text.

Tool execution is controlled by deterministic, rule-based intent detection.

```text
User Input
    ↓
Intent Detection
    ↓
Known Tool?
    ↓
Validation
    ↓
Approved Python Tool
    ↓
Result
```

The LLM does not directly execute system commands.

---

### 2. No Shell Access

The project does not use:

```python
os.system()
```

or:

```python
subprocess
```

for arbitrary command execution.

User or LLM-generated text is never passed to a system shell.

---

### 3. Website Whitelist

Only four websites are approved:

* Google
* YouTube
* GitHub
* LinkedIn

The user's input is used as a dictionary key rather than being treated as an arbitrary URL.

For example:

```text
open google
```

maps to a predefined website entry.

An unsupported request such as:

```text
open cmd
```

is rejected.

---

### 4. Notes Are Jailed

All note operations are restricted to:

```text
data/notes/
```

The application performs:

* Filename validation
* Resolved-path validation
* Workspace restriction

Notes are never overwritten.

---

### 5. Tool Results Are Shown Verbatim

Tool results are returned directly to the user.

The LLM cannot rephrase a failed tool operation into a fake success message.

For example, if a note cannot be created, the actual failure is shown instead of claiming that the note was successfully created.

---

### 6. No Secrets in Code

Configuration such as the selected model is stored in `.env`.

The `.env` file should be excluded from Git using `.gitignore`.

Example:

```text
.env
```

---

## Limitations

* Local model quality and speed depend on:

  * Computer hardware
  * Available RAM
  * Model size
* Rule-based intent detection is fast and safe but can be brittle.
* Unusual command phrasings may fall through to the LLM.
* The assistant has **no real-time knowledge**.
* The assistant has **no actual web retrieval**.
* The web-search tool only opens a search page in the browser.
* Conversation memory is short-term only.
* The default memory contains the last **16 messages**.
* Tool capabilities are intentionally restricted.
* The assistant is not a fully autonomous agent.
* RAG is not implemented.

---

## Future Enhancements

The following features are **not implemented** in the current version.

### 1. Voice Input and Output

Integrate voice recognition and text-to-speech to allow spoken interaction.

### 2. RAG

Add Retrieval-Augmented Generation for answering questions from uploaded documents.

Possible use cases:

* PDF question answering
* Company documents
* Project documentation
* Knowledge bases

### 3. Long-Term Memory

Store user preferences, summaries, and important conversation information for future sessions.

### 4. Calendar and Email Integration

Add controlled integrations for:

* Calendar events
* Email drafting
* Reminders

### 5. Structured LLM Tool Calling

Replace rule-based keyword detection with structured LLM tool-calling while maintaining strict validation and permissions.

### 6. More Tools

Add additional safe tools such as:

* Calculator
* File utilities
* Weather
* Reminders
* System monitoring

### 7. Scheduled Automation

Allow users to schedule approved tasks for specific times.

### 8. Multimodal Input

Add support for image input and other forms of multimodal interaction.

---

## Project Scope

The current project intentionally focuses on a simple and safe architecture:

```text
                  Smart AI Assistant
                         │
          ┌──────────────┴──────────────┐
          │                             │
          ▼                             ▼
   Question Answering             Task Execution
          │                             │
          ▼                             ▼
    Local Ollama LLM             Python Tools
          │                             │
          ▼                             ▼
 Short-Term Memory            Whitelist + Validation
                                        │
                                        ▼
                                 Safe Automation
```

This separation makes the project easier to understand, test, and extend while keeping automation under deterministic control.

---

## Conclusion

This project delivered a **local LLM-powered Smart AI Assistant** capable of both conversational question answering and basic task automation.

The project demonstrates several important concepts:

* Local LLM inference using Ollama
* Prompt engineering
* Short-term conversation memory
* Rule-based intent detection
* Python-based tool execution
* Website whitelisting
* Safe file handling
* Path validation
* Browser automation
* Optional Streamlit interface
* Graceful error handling

A key design principle of the project is the separation between **conversation and task execution**. The local LLM handles general questions, while deterministic Python tools perform only predefined and validated actions.

The assistant is intentionally described accurately: it does **not** use RAG, autonomous agents, real-time web retrieval, or unrestricted system execution. These capabilities are reserved for future enhancements.

This project provides a practical foundation for developing more advanced AI assistants while maintaining clear boundaries between **LLM-generated responses** and **safe, deterministic automation**.

---

## Author

**Sandhiya**
**AI/ML Intern – RaushByte Technologies**
