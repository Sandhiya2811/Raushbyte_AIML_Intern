# Project Report — Smart AI Assistant using Python and LLM

**Internship:** AI/ML Internship
**Organization:** RaushByte Technologies
**Task:** Level 3 – Task 1: Smart AI Assistant
**Prepared By:** Sandhiya
---

## 1. Introduction

A **conversational AI assistant** is a system that communicates with users in natural language. Modern assistants combine two abilities:

1. **Question answering** — understanding a question and producing a helpful answer, which is the job of Large Language Models.
2. **Task execution** — performing real actions such as opening a website or saving a file, which is the job of programmatic tools.

This project builds an assistant that combines both capabilities using a **locally installed Ollama LLM** for conversation and a **safe, whitelisted Python tool layer** for tasks, with a clear architectural separation between the two.

---

## 2. Problem Statement

Chat-only assistants cannot perform actions, while script-only automation cannot converse.

A practical assistant needs to:

1. Understand natural-language questions, including follow-up questions that rely on context.
2. Decide when a request is a **task** rather than a question.
3. Execute tasks safely without exposing shell access or arbitrary file operations to untrusted input.
4. Fail gracefully when the LLM is unavailable.

Small local models make this harder because they must never be trusted to report actions accurately.

---

## 3. Objective

The objectives of this project are to:

1. Answer general questions using a local Ollama LLM.
2. Maintain short-term conversation memory for follow-up questions.
3. Perform predefined tasks:

   * Time
   * Date
   * Approved websites
   * Browser search
   * Notes — create, read, and list
4. Map multiple natural-language phrasings to the same tool.
5. Keep task execution deterministic and safe using:

   * Whitelists
   * Path jailing
   * No shell access
   * No LLM-triggered actions
6. Handle errors gracefully, including:

   * Ollama being unavailable
   * Model not being installed
   * Invalid input

---

## 4. Technologies Used

| Technology                                    | Purpose                                                                                    |
| --------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Python 3**                                  | Core application                                                                           |
| **Ollama**                                    | Local LLM runtime; the `ollama` Python package connects to it at `http://localhost:11434`  |
| **LLM (configurable, default `llama3.2:3b`)** | Natural-language question answering                                                        |
| **Prompt Engineering**                        | Defines personality, conciseness, honesty about uncertainty, and strict operational limits |
| **python-dotenv**                             | Loads `.env` configuration such as model name, base URL, and memory limit                  |
| **datetime**                                  | Provides real date and time values                                                         |
| **webbrowser**                                | Opens approved websites and browser search pages                                           |
| **pathlib**                                   | Provides safe file and path handling for notes                                             |
| **urllib.parse**                              | Supports safe encoding of browser-search queries                                           |
| **Streamlit**                                 | Optional web interface over the same controller                                            |

---

## 5. System Architecture

```text id="o2w8by"
User
  ↓
Conversation Interface
(console: assistant.py / Streamlit: app.py)
  ↓
Assistant Controller
(handle_user_message)
  ↓
Intent / Tool Decision
(rule-based detect_intent)
  │
  ├── Question
  │      ↓
  │   LLM
  │   (Ollama + system prompt + memory)
  │
  └── Task
         ↓
      Tool Layer
      (execute_tool)
         │
         ├── get_current_time()
         ├── get_current_date()
         ├── open_website()
         │      └── Whitelist
         ├── search_web()
         │      └── Browser only
         └── Notes
                ├── create
                ├── read
                └── list
                └── Jailed to data/notes/

                ↓
          Tool Result
          (shown verbatim,
           stored in memory)
                ↓
        Assistant Response
                ↓
               User
```

### Why This Architecture?

The LLM and the tools are completely separate modules.

The only bridge between them is the controller, which decides **deterministically** which side handles each message.

```text
LLM → Question Answering
Tools → Task Execution
Controller → Deterministic Routing
```

This prevents the LLM from directly triggering an action.

---

## 6. LLM Integration

The `llm.py` module creates an `ollama.Client` using `OLLAMA_BASE_URL` from the configuration.

The `check_connection()` function verifies:

1. Whether Ollama is reachable.
2. Whether the configured `OLLAMA_MODEL` is installed.

The model is matched using either the exact model name or its base tag.

If the model is missing, the assistant provides a friendly and actionable message such as:

```text
ollama pull llama3.2:3b
```

A failed connection check is **not fatal**.

The tool layer can continue working even when Ollama is unavailable.

The `generate_reply()` function:

1. Sends the system prompt.
2. Includes recent conversation history.
3. Sends the request to the configured local model.
4. Returns the model's response.
5. Returns a friendly error if generation fails.

The model name is never hardcoded in the application code. It is loaded from `.env`.

---

## 7. Prompt Engineering

The system prompt in `llm.py` defines the assistant's behavior.

### Role and Tone

* Helpful
* Professional
* Concise
* Friendly

### Behavior

* Provides beginner-friendly explanations.
* Keeps answers short by default.
* Is honest about uncertainty.
* Uses conversation history for follow-up questions.

### Strict Operational Limits

The LLM is instructed that it:

* Cannot know the current date or time.
* Cannot open websites.
* Cannot perform web searches.
* Cannot create files.
* Cannot read files.
* Cannot perform system actions.
* Must direct users to the appropriate direct command for tasks.

### Anti-Fabrication Rule

The prompt explicitly instructs the model:

> **"NEVER claim you performed an action, and never pretend an action succeeded."**

This rule is also reinforced structurally.

Tool results bypass the LLM entirely, so even if a model ignores the instruction, it cannot misreport an action's outcome.

---

## 8. Conversation Memory

Short-term memory is maintained as a list of messages:

```python
[
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
]
```

Each exchange is appended to the conversation history.

This includes:

* User messages
* Assistant responses
* Tool results

The history is then trimmed to the last `HISTORY_LIMIT` messages.

The default is:

```text
HISTORY_LIMIT = 16
```

The value can be configured.

### Example

The user can first ask:

```text
What is machine learning?
```

and then ask:

```text
Give me a simple example.
```

Because recent conversation history is included in the next LLM request, the assistant can understand that `"it"` or `"a simple example"` refers to the previous topic.

### Memory Limitation

Because the list is capped, memory cannot grow indefinitely during long sessions.

---

## 9. Tool Layer

| Tool                                        | Action                          | Safety                                                                                                     |
| ------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `get_current_time()` / `get_current_date()` | Returns live `datetime` values  | LLM never guesses these values                                                                             |
| `open_website(name)`                        | Opens an approved website       | Input is a dictionary key, never a URL; four approved sites only                                           |
| `search_web(query)`                         | Opens a Google search page      | Browser-opening only; no retrieval or reading of results                                                   |
| `create_note(filename, content)`            | Writes a note to `data/notes/`  | Filename validation, resolved-path check, refuses overwrite, timestamped name when no filename is supplied |
| `read_note(filename)`                       | Reads a note from `data/notes/` | Same path validation; friendly `"not found"` response                                                      |
| `list_notes()`                              | Lists saved notes               | Read-only                                                                                                  |
| `execute_tool(name, args)`                  | Routes a requested tool         | Unknown tools are rejected; catch-all exception guard                                                      |

---

### Tool Selection Method

Tools are selected through **rule-based intent detection**.

The system uses:

* Ordered phrase matching
* Whole-word boundaries
* Prefix parsing for arguments
* Anchored regular expressions for note commands

This is **not machine learning**.

It is deterministic keyword and phrase matching.

### Why Rule-Based Routing?

Rule-based routing was selected instead of LLM tool-calling because small local models can be unreliable when generating structured tool calls.

Deterministic routing guarantees that the LLM cannot directly trigger an action.

> **Future enhancement:** LLM-based structured tool calling can be added later with appropriate validation and permission controls.

---

## 10. Safety Architecture

Unrestricted shell execution is avoided because LLM output and user text are treated as **untrusted input**.

Executing something such as:

```python
os.system(llm_output)
```

or:

```python
subprocess.run(..., shell=True)
```

could allow arbitrary command injection.

This project contains:

* No `os.system()`
* No `subprocess`
* No arbitrary shell execution

Instead, it uses the following safety mechanisms.

### 1. Deterministic Dispatch

Only `detect_intent()` can identify a tool.

Only `execute_tool()` can execute a tool.

```text
User Input
    ↓
detect_intent()
    ↓
Approved Tool?
    ↓
execute_tool()
    ↓
Tool Result
```

---

### 2. Website Whitelists

Websites come from a fixed four-entry dictionary.

The user cannot provide an arbitrary URL to the tool.

---

### 3. Path Jailing

Note operations:

1. Validate the filename.
2. Construct the path.
3. Resolve the path.
4. Verify that the resolved path remains inside:

```text
data/notes/
```

This prevents path traversal outside the allowed directory.

---

### 4. No Overwrites

Existing notes are never replaced.

If a requested note already exists, the operation is refused.

---

### 5. Verbatim Tool Results

Tool results are displayed exactly as produced.

The LLM cannot transform a failure into a claimed success.

For example:

```text
Tool → Note could not be found.
```

is shown to the user as a failure rather than being sent back to the LLM for interpretation.

---

### 6. System-Prompt Guardrails

The LLM is instructed to:

* Refuse unsafe requests.
* Never claim that it performed an action.
* Never pretend an action succeeded.
* Direct users to the appropriate task commands.

---

## 11. Implementation

The application is organized into small, focused components.

### Key Functions

| Function                | Responsibility                                               |
| ----------------------- | ------------------------------------------------------------ |
| `detect_intent()`       | Performs ordered rule-based intent detection                 |
| `handle_user_message()` | Routes the user's message to either the LLM or tool layer    |
| `_safe_note_path()`     | Performs defense-in-depth path validation                    |
| `check_connection()`    | Checks Ollama availability and model installation            |
| `generate_reply()`      | Sends conversation history and system instructions to Ollama |
| `execute_tool()`        | Executes only approved tools                                 |
| `app.py`                | Provides the Streamlit interface                             |

### Intent Detection

`detect_intent()` uses ordered rules.

It includes:

* Politeness stripping
* Whole-word matching
* Prefix parsing
* Specific time/date patterns

For example:

```text
please open github
```

is correctly recognized as a website task.

The system also distinguishes:

```text
what is the time?
```

from:

```text
what is time complexity?
```

so that a question about time complexity is not incorrectly treated as a request for the current time.

### Conversation Handling

`handle_user_message()`:

1. Appends the user's message before the LLM call.
2. Sends the recent conversation history to the LLM.
3. Receives the response.
4. Appends the assistant response.
5. Trims the history according to `HISTORY_LIMIT`.

### Shared Controller

The Streamlit interface reuses:

```python
handle_user_message()
```

from the same controller used by the console interface.

This provides:

```text
One Controller
     │
     ├── Console Interface
     │
     └── Streamlit Interface
```

Therefore, both interfaces use the same intent detection, LLM integration, and tool execution logic.

---

## 12. Testing

> **Testing Requirement:** Run each test yourself and record the actual result. The **Status** column is intentionally left blank. No test should be marked as passed before it is actually executed.

| Test Case                  | Input                                                    | Expected Result                              | Status   |
| -------------------------- | -------------------------------------------------------- | -------------------------------------------- | -------- |
| General question           | `What is AI?`                                            | LLM provides an answer                       | *(fill)* |
| Follow-up                  | `Explain it simply`                                      | Context-aware answer                         | *(fill)* |
| Memory — `"its"` reference | `What is Python?` → `What are its advantages?`           | Second answer refers to Python               | *(fill)* |
| Time                       | `What time is it?`                                       | Current time using a real value              | *(fill)* |
| Date                       | `What is today's date?`                                  | Current date using a real value              | *(fill)* |
| Website                    | `Open GitHub`                                            | Approved website opens                       | *(fill)* |
| Unapproved site            | `Open cmd`                                               | Refusal + allowed website list               | *(fill)* |
| Search                     | `search Python decorators`                               | Search page opens in browser                 | *(fill)* |
| Note create                | `Create a note called interview.txt with: Revise Python` | Note saved in `data/notes/`                  | *(fill)* |
| Note read                  | `Read interview.txt`                                     | Note content displayed                       | *(fill)* |
| Notes list                 | `list notes`                                             | Numbered note list displayed                 | *(fill)* |
| Missing note               | `read note missing.txt`                                  | Friendly `"not found"` response              | *(fill)* |
| Shell-like input           | `run del C:\Windows`                                     | Command is not executed; safe refusal/answer | *(fill)* |
| Invalid request            | Unsupported command                                      | Safe fallback with no invented success       | *(fill)* |
| Ollama stopped             | Stop Ollama and ask a question                           | Friendly error; tools continue to work       | *(fill)* |
| Exit                       | `exit`                                                   | Application closes cleanly                   | *(fill)* |

---

## 13. Results

> **Update this section with your actual observed results after testing.**

The assistant is designed to:

* Answer general questions through the local LLM.
* Resolve follow-up questions using conversation memory.
* Report real date and time values.
* Open only approved websites.
* Open browser search pages.
* Create, read, and list notes strictly inside `data/notes/`.
* Display tool results verbatim.
* Report tool failures as failures rather than fabricated successes.
* Continue providing available tool functionality when Ollama is unavailable.

After executing the complete test suite, the actual results and screenshots should be added to this section.

---

## 14. Limitations

* Local model quality varies depending on:

  * Model selection
  * Computer hardware
  * Available memory
* Generation speed depends on the computer and selected model.
* There is no real-time knowledge.
* The assistant cannot know current events unless a real retrieval tool is implemented.
* No web retrieval is implemented.
* The search tool only opens a search page; it does not retrieve or read the results.
* Rule-based intent detection can be brittle for unusual phrasings.
* The deterministic routing approach is an intentional trade-off for safety and predictability.
* Tool capabilities are intentionally restricted.
* Conversation memory is short-term only.

---

## 15. Privacy and Security

### Local Processing

All LLM inference occurs locally through Ollama.

There are:

* No cloud LLM APIs.
* No paid AI services.
* No external LLM data processing.

Opening a website or search page is performed through the user's own browser.

### No Unnecessary Data Collection

Conversation history exists only in memory and is cleared when the application closes.

Notes are stored only in the designated notes directory.

### Restricted File Access

The only writable location for notes is:

```text
data/notes/
```

This is enforced using filename validation and resolved-path checks.

### No Arbitrary Command Execution

The application contains no shell execution functionality.

User input and LLM output cannot be executed as system commands.

### No Secrets in Source Code

Configuration is loaded from the `.env` file.

The `.env` file should be excluded from version control using `.gitignore`.

Example:

```text
.env
```

---

## 16. Future Enhancements

### RAG

Implement Retrieval-Augmented Generation to answer questions from uploaded documents.

Possible use cases include:

* PDF question answering
* Project documentation
* Company knowledge bases
* Technical documents

### Voice Mode

Integrate:

```text
Speech-to-Text
      ↓
LLM
      ↓
Tools
      ↓
Text-to-Speech
```

### Long-Term Memory

Store:

* User preferences
* Important facts
* Conversation summaries

### Structured LLM Tool Calling

Replace keyword-based rules with structured tool definitions while maintaining:

* Permission checks
* Input validation
* Tool whitelisting
* Safe execution

This would represent a genuine architectural upgrade.

### Calendar and Email Integrations

Add controlled integrations for:

* Calendar events
* Email drafting
* Reminders

### More Tools

Expand the assistant with additional safe tools.

### Scheduled Automation

Allow approved tasks to run at predefined times.

### Multimodal Input

Add support for:

* Images
* Screenshots
* Other multimodal inputs

---

## 17. Conclusion

This project delivered an **LLM-powered Smart AI Assistant** combining two clearly separated capabilities:

```text
                 Smart AI Assistant
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
    Question Answering          Task Execution
            │                         │
            ▼                         ▼
      Local Ollama LLM          Python Tool Layer
            │                         │
            ▼                         ▼
    Short-Term Memory          Whitelist + Validation
                                      │
                                      ▼
                              Safe Deterministic
                                  Automation
```

The local Ollama model provides question answering and short-term conversational memory, while the deterministic Python tool layer handles predefined tasks such as date/time, approved websites, browser search, and notes.

The most important learning from this project was **architectural separation**: understanding and acting are treated as different responsibilities.

The project also demonstrates why LLM output should never be treated as executable instruction. User and model text are treated as untrusted input, while only deterministic rules can select approved tools.

Another important design principle is **verbatim tool results**. By keeping tool results outside the LLM's response-generation path, the assistant cannot turn a failed action into a fabricated success.

Finally, the project is described accurately:

* It uses an LLM for question answering.
* It uses rule-based intent mapping for task routing.
* It does not use ML-based intent classification.
* It does not implement agents.
* It does not implement RAG.
* It does not perform real-time web retrieval.
* It does not provide unrestricted system access.

This project builds on the foundations of my **Level 1 rule-based chatbot** and **Level 2 desktop automation work**, combining those concepts into a larger, locally hosted, LLM-centered assistant with a strong focus on safety and deterministic task execution.
