# Rule-Based AI Chatbot using Python

**Internship:** AI/ML Internship
**Organization:** RaushByte Technologies
**Task:** Level 1 – Task 2 (Basic Chatbot Build)
**Prepared By:** [Sandhiya]

---

## 📌 About the Project

This is a simple **rule-based chatbot** built entirely in Python. It runs in the terminal/console, listens to what the user types, matches the input against a set of **predefined keywords and phrases**, and replies with the matching **predefined response**.

If the input is not recognized, it responds politely with a fallback message instead of crashing.

It was developed as **Level 1 – Task 2** of the AI/ML Internship at **RaushByte Technologies**, to demonstrate the core concept of rule-based conversational systems — the foundation on which more advanced **NLP/ML-based chatbots** are built.

---

## 🎯 Objective

* Accept user input from the terminal
* Identify predefined keywords or phrases
* Respond with appropriate predefined answers
* Handle greetings, basic questions, help requests, and unknown input
* Allow the user to exit the chat cleanly
* Do all of this using **only Python and its standard library**

---

## ✨ Features

* ✅ Greets the user
  *(hello / hi / hey / good morning / good afternoon / good evening)*

* ✅ Introduces itself
  *(who are you?)*

* ✅ Tells the user its name
  *(what is your name?)*

* ✅ Provides a help menu
  *(help / what can you do? / commands)*

* ✅ Answers basic questions about **AI, Machine Learning, and Python**

* ✅ Explains what an **internship** is

* ✅ Answers **"what is RaushByte?"** using only information provided in the task

* ✅ Provides polite responses to **"thank you"**

* ✅ Provides a graceful fallback for unknown inputs

* ✅ **Case-insensitive matching**
  `HELLO = hello = HeLLo`

* ✅ Ignores **extra spaces** and **punctuation**

* ✅ Handles empty input
  `"Please enter a message."`

* ✅ Clean exit using:

  * `bye`
  * `exit`
  * `quit`
  * `goodbye`

* ✅ Safe **Ctrl+C** handling

* ✅ No external APIs

* ✅ No Machine Learning models

* ✅ No third-party dependencies

---

## 🛠️ Technologies Used

| Technology   | Purpose                                               |
| ------------ | ----------------------------------------------------- |
| **Python 3** | Programming language                                  |
| `random`     | Picks a varied greeting, farewell, or thanks response |
| `string`     | Removes punctuation during input cleaning             |

> **Note:** No third-party package installation is required.

---

## ⚙️ How It Works

The chatbot follows a simple rule-based processing flow:

```text
User Input
    ↓
Input Preprocessing
(lowercase → strip spaces → remove punctuation)
    ↓
Rule Matching
(check exit phrases, then topic rules, in order)
    ↓
Match Found?
   /       \
 Yes        No
  ↓          ↓
Predefined  Fallback
 Response    Response
      \      /
       ↓
Display Response
       ↓
Exit Command?
   /       \
 Yes        No
 ↓          ↓
Stop     Continue Loop
```

### 🔍 Whole-Word Matching

A small but important detail is that patterns are matched as **whole words** by padding both the input and the pattern with spaces.

This prevents:

```text
hi
```

from falsely matching inside:

```text
this
```

Similarly:

```text
ai
```

will not falsely match inside:

```text
train
```

This makes the keyword matching more reliable.

---

## 📁 Project Structure

```text
raushbyte-basic-chatbot/
│
├── README.md
│
├── chatbot/
│   └── chatbot.py
│
├── screenshots/
│   └── chatbot_demo.png
│
└── docs/
    └── chatbot_report.md
```

### File Description

| File / Folder                  | Description                       |
| ------------------------------ | --------------------------------- |
| `README.md`                    | Project documentation             |
| `chatbot/chatbot.py`           | Main chatbot program              |
| `screenshots/chatbot_demo.png` | Terminal demonstration screenshot |
| `docs/chatbot_report.md`       | Mini technical report             |

---

## 💻 Installation

### Step 1 — Install Python

Download and install **Python 3.8+** from:

**https://www.python.org/downloads/**

> **Windows users:** Make sure to tick **"Add Python to PATH"** during installation.

### Step 2 — Verify Python Installation

Open PowerShell or Command Prompt and run:

```powershell
python --version
```

Example:

```text
Python 3.12.5
```

### Step 3 — Download or Clone the Project

Clone or download the repository.

No additional setup or package installation is required.

---

## ▶️ How to Run

### From the Project Root Folder

Open **Windows PowerShell** inside the project folder and run:

```powershell
python chatbot/chatbot.py
```

### From Inside the `chatbot` Folder

Run:

```powershell
cd chatbot
python chatbot.py
```

> On some systems, the command may be `python3` instead of `python`.

---

## 🧑‍💻 Running in VS Code

1. Open the project folder in **VS Code**
2. Open:

```text
chatbot/chatbot.py
```

3. Open the integrated terminal using:

```text
Ctrl + `
```

4. Run:

```powershell
python chatbot/chatbot.py
```

5. Alternatively, click the **▶ Run** button in VS Code.

---

## 💬 Example Conversation

> **Note:** Greeting and farewell responses may vary slightly because the chatbot randomly selects responses from a few predefined options.

```text
==================================================
           RULE-BASED AI CHATBOT
          RaushByte Technologies
==================================================

Chatbot: Hello! I am ByteBot, a Rule-Based AI Chatbot.
Chatbot: Type 'help' to see what I can do.

You: HELLO

Chatbot: Hello! Nice to meet you. How can I help you today?

You: what is AI?

Chatbot: Artificial Intelligence (AI) is the ability of machines or
computer systems to perform tasks that normally require human
intelligence, such as understanding language, recognizing images,
and making decisions.

You: what is python?

Chatbot: Python is a high-level, easy-to-learn programming language.
It is widely used in AI, Machine Learning, Data Science, web
development, and automation.

You: what is the weather today?

Chatbot: I'm sorry, I don't understand that yet. Please try asking
about AI, Machine Learning, Python, or internships - or type 'help'
to see what I can do.

You: thank you

Chatbot: You're welcome! Is there anything else I can help you with?

You: bye

Chatbot: Goodbye! Have a great day.

==================================================
           Chatbot session ended.
==================================================
```

---

## ⚠️ Limitations

* It only understands **predefined inputs** and close variations of them.
* It **cannot understand complex or open-ended questions**.
* It **does not learn** from conversations.
* Its behavior never changes based on previous conversations.
* It **does not use Machine Learning**.
* It uses pure **keyword/phrase matching**.
* It **cannot generate dynamic answers**.
* Every response is **hardcoded**.
* Its knowledge is limited to the rules programmed into it.
* Word matching can occasionally misfire.

### Example

The input:

```text
I don't want to quit my internship
```

could potentially trigger the `quit` exit command.

---

## 🚀 Future Improvements

The following improvements are **not implemented in this task**, but could be added in future versions:

* NLP-based intent detection

  * Tokenization
  * TF-IDF similarity

* Machine Learning-based text classification

* Database integration for a larger and editable knowledge base

* Voice input

* Text-to-speech output

* Web interface using:

  * Flask
  * Streamlit

* LLM integration for advanced conversational capabilities

* Context-aware conversations

* Memory of previous user messages

---

## 📝 Acknowledgment

This chatbot was developed as part of the **AI/ML Internship at RaushByte Technologies**, specifically for:

> **Level 1 – Task 2: Basic Chatbot Build**

Thank you to **RaushByte Technologies** for providing the opportunity to learn and demonstrate the fundamentals of conversational AI.
