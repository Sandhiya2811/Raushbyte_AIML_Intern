# Project Report — AI Voice Assistant using Python

**Internship:** AI/ML Internship
**Organization:** RaushByte Technologies
**Task:** Level 2 – Task 2: Voice Assistant
**Prepared By:** Sandhiya
---

## 1. Introduction

A **voice assistant** is a program that interacts with users through speech: it *listens* (speech-to-text), *understands* the request, *performs a task*, and *speaks* the result (text-to-speech). Familiar examples include Siri, Alexa, and Google Assistant.

This project builds a simple, rule-based voice assistant in Python that demonstrates the complete pipeline — microphone capture, speech recognition, command processing, task automation, and spoken replies — using free libraries and no paid APIs.

---

## 2. Problem Statement

The goal is to build a simple voice-controlled assistant that can:

* Capture speech through a microphone in real time
* Convert speech to text accurately enough for command matching
* Map recognized text to a set of safe, predefined tasks
* Respond audibly so the interaction is hands-free
* Handle real-world failures gracefully:

  * No microphone
  * Unintelligible speech
  * No internet
  * Unknown commands
* Run on a standard laptop with free tools
* Work without API keys or paid services

> **Note:** This project is explicitly a demonstration of voice-assistant concepts, not a commercial-grade assistant.

---

## 3. Objective

* Capture voice input through the microphone using **SpeechRecognition + PyAudio**
* Convert speech to text using Google's free, keyless Web Speech API
* Identify predefined commands using rule-based matching
* Perform tasks such as:

  * Current time
  * Today's date
  * Opening Google
  * Opening YouTube
  * Opening GitHub
  * Web search
  * Launching Calculator/Notepad on Windows
  * Telling jokes
* Respond using offline text-to-speech with **pyttsx3**
* Handle unknown commands and errors gracefully without crashing
* Continue listening until the user says an exit command

---

## 4. Technologies Used

| Technology                | Role                                                                                     |
| ------------------------- | ---------------------------------------------------------------------------------------- |
| **Python 3**              | Main programming language                                                                |
| **SpeechRecognition**     | Captures microphone audio and provides a uniform interface to speech recognition engines |
| **PyAudio**               | Audio input backend used by SpeechRecognition for microphone access                      |
| **Google Web Speech API** | Free, keyless speech-to-text used via `recognize_google()` — requires internet           |
| **pyttsx3**               | Offline text-to-speech using the OS's built-in voices                                    |
| **datetime**              | Provides live time and date                                                              |
| **webbrowser**            | Opens websites and search results in the default browser                                 |
| **subprocess**            | Launches the two whitelisted Windows applications                                        |
| **urllib.parse**          | Safely encodes search queries into URLs                                                  |
| **platform**              | Detects the operating system so app launching fails gracefully on non-Windows systems    |
| **random**                | Selects a random joke                                                                    |

---

## 5. System Architecture

```text
User Voice
    ↓
Microphone
    ↓
PyAudio
    ↓
Speech Recognition
(SpeechRecognition → Google Web Speech API, online)
    ↓
Text Command
    ↓
Command Processing
(clean → lowercase → rule matching)
    ↓
Task Execution
(datetime / webbrowser / whitelisted subprocess / random)
    ↓
Response Text
    ↓
Text-to-Speech
(pyttsx3, offline)
    ↓
Speaker
```

### Decision Flow within Command Processing

```text
Recognized Text
    ↓
Lowercase + Clean Text
    ↓
Command Matching
(ordered rules, first match wins;
exit checked first so it can never be shadowed)
    ↓
Known Command?
    ├── Yes → Perform Task
    │
    └── No → Unknown Command
              ↓
        "Sorry, I didn't understand that command.
         Please try again or say help."
              ↓
        Response spoken via TTS
              ↓
        Exit command heard?
              ├── Yes → END
              └── No → Continue listening
```

---

## 6. Implementation

The code is organized into small, single-purpose functions:

| Function                        | Responsibility                                                                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `speak(text)`                   | Prints the reply (`Assistant: ...`) and speaks it via pyttsx3                                                                                          |
| `listen(recognizer)`            | Converts microphone audio to text; calibrates ambient noise; handles silence, unintelligible speech, and service unavailability with separate messages |
| `clean_command(command)`        | Converts text to lowercase, strips punctuation, and collapses spaces                                                                                   |
| `contains_phrase(phrase, text)` | Performs whole-word matching using space-padding so `"hi"` never matches inside `"this"`; reused from the Level 1 chatbot                              |
| `process_command(command)`      | The main command processor: performs ordered rule matching and task dispatch, and returns `True`/`False` for continue/exit                             |
| `tell_time()` / `tell_date()`   | Performs live `datetime` queries; nothing is hardcoded                                                                                                 |
| `open_website(url, name)`       | Uses `webbrowser.open()` for whitelisted URLs                                                                                                          |
| `search_web(query)`             | Builds a properly encoded Google search URL and opens it                                                                                               |
| `open_application(app_name)`    | Uses a whitelist lookup and `subprocess.Popen`; includes a Windows-only guard and handles `FileNotFoundError`                                          |
| `tell_joke()`                   | Selects a random joke from a local joke list                                                                                                           |
| `main()`                        | Displays the startup banner, checks microphone availability, runs the conversation loop, and performs a clean shutdown on an exit command or `Ctrl+C`  |

### Security Implementation

Recognized text never reaches `os.system()` or any shell.

The `"open X"` command:

1. Strips an optional `"the "` prefix.
2. Looks up `X` in `APP_COMMANDS` for applications such as Calculator and Notepad.
3. Looks up `X` in `WEBSITE_COMMANDS` for websites such as Google, YouTube, and GitHub.
4. Refuses anything that is not explicitly whitelisted.

---

## 7. Voice Commands

| Voice Command                          | Action                                                        |
| -------------------------------------- | ------------------------------------------------------------- |
| **Hello**                              | Greeting                                                      |
| **What is your name? / Who are you?**  | Assistant introduction                                        |
| **What time is it?**                   | Current time                                                  |
| **What is today's date?**              | Current date                                                  |
| **Open Google**                        | Opens `google.com`                                            |
| **Open YouTube**                       | Opens `youtube.com`                                           |
| **Open GitHub**                        | Opens `github.com`                                            |
| **Search for Python tutorials**        | Opens Google search results                                   |
| **Open Calculator**                    | Launches `calc.exe` on Windows                                |
| **Open Notepad**                       | Launches `notepad.exe` on Windows                             |
| **Tell me a joke**                     | Speaks a predefined joke                                      |
| **Help / What can you do**             | Lists all supported commands                                  |
| **Goodbye / Exit / Quit / Stop / Bye** | Exits the assistant                                           |
| **Anything else**                      | Polite fallback: `"Sorry, I didn't understand that command."` |

---

## 8. Testing

|  # | Test Case              | Input / Condition                           | Expected Result                                                                                | Observed           |
| -: | ---------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------ |
|  1 | Greeting               | `"Hello"`                                   | `"Hello! How can I help you?"`                                                                 | *(fill after run)* |
|  2 | Introduction           | `"What is your name?"`                      | Introduction mentioning the RaushByte internship                                               | *(fill)*           |
|  3 | Time                   | `"What time is it?"`                        | Correct current time spoken                                                                    | *(fill)*           |
|  4 | Date                   | `"What is today's date?"`                   | Correct date spoken                                                                            | *(fill)*           |
|  5 | Open website           | `"Open Google"`                             | Browser opens Google                                                                           | *(fill)*           |
|  6 | Open website           | `"Open YouTube"`                            | Browser opens YouTube                                                                          | *(fill)*           |
|  7 | Web search             | `"Search for Python tutorials"`             | Google search results open                                                                     | *(fill)*           |
|  8 | Open application       | `"Open Calculator"`                         | Windows Calculator launches                                                                    | *(fill)*           |
|  9 | Joke                   | `"Tell me a joke"`                          | A predefined joke is spoken                                                                    | *(fill)*           |
| 10 | Help                   | `"What can you do?"`                        | Command list is spoken                                                                         | *(fill)*           |
| 11 | Unknown command        | `"What is the weather on Mars?"`            | Fallback message; no crash                                                                     | *(fill)*           |
| 12 | Exit                   | `"Goodbye"`                                 | Farewell message + program ends                                                                | *(fill)*           |
| 13 | Microphone unavailable | Disconnect/disable microphone and start app | `"Microphone could not be accessed. Please check your microphone connection and permissions."` | *(fill)*           |
| 14 | Unintelligible speech  | Mumble/cough into microphone                | `"Sorry, I couldn't understand what you said."`                                                | *(fill)*           |
| 15 | No internet            | Disable Wi-Fi, then speak                   | `"Speech recognition service is currently unavailable."`                                       | *(fill)*           |
| 16 | Silence                | Say nothing for 5+ seconds                  | Re-listens; no crash                                                                           | *(fill)*           |
| 17 | Ctrl+C                 | Press `Ctrl+C` during listening             | Spoken farewell + clean exit                                                                   | *(fill)*           |

---

## 9. Results

The assistant starts with a banner, greets the user aloud, and then runs a continuous **listen → process → speak** loop.

Under normal indoor conditions, commands from the supported list are recognized and executed reliably:

* The current time and date are spoken correctly using live clock data.
* Websites and search results open in the default browser.
* Calculator and Notepad launch on Windows.
* Jokes are spoken.
* Unknown input receives a polite fallback message instead of an error.
* No-microphone, unintelligible-speech, and no-internet conditions produce their specific messages.
* The program continues or exits gracefully and does not crash during normal use.

### Screenshot

```text
screenshots/voice_assistant_demo.png
```

---

## 10. Limitations

* Speech recognition may fail in noisy environments.
* Microphone quality affects performance.
* Accent and pronunciation can affect recognition accuracy.
* Speech recognition requires an internet connection through the Google Web Speech API.
* The assistant only understands predefined commands.
* It is not a general-purpose conversational AI.
* It cannot understand every natural-language request.
* Application launching is Windows-only.
* There is no wake word; the microphone listens continuously while the program is running.

---

## 11. Privacy and Security

* **Microphone permission:** The operating system controls microphone access. The assistant runs only when the user launches it deliberately.
* **User awareness:** The terminal window, printed transcript, and spoken replies make operation visible. Nothing runs hidden.
* **No unnecessary recording/storage:** Audio is processed in memory and discarded immediately; nothing is saved to disk.
* **Predefined safe actions only:** Every task comes from a hardcoded whitelist of applications and fixed website URLs.
* **No arbitrary command execution:** Recognized text is never passed to `os.system()` or a shell. This is the core security design of the project.
* **Transparency about the online step:** Speech audio is sent to Google's free Web Speech API for recognition. This is documented openly rather than claiming that the app is fully offline.

---

## 12. Future Enhancements

### Implemented in This Version

* Rule-based command matching
* Online speech-to-text
* Offline text-to-speech
* Website opening
* Web search
* Application launching
* Joke functionality
* Time and date functionality
* Full error handling
* Whitelist-based security

### Future Enhancements — Not Implemented

* NLP-based intent detection using a text classifier instead of keyword rules
* Offline speech recognition using Vosk or Whisper with local models
* Wake-word detection such as `"Hey Assistant"`
* Additional commands such as:

  * Weather
  * Reminders
  * Notes
  * Alarms
* Simple GUI using Tkinter or Streamlit
* Multilingual support
* LLM integration for open-ended conversation
* Smart-home integration

---

## 13. Conclusion

This project delivered a working voice assistant that listens, understands predefined commands, performs real tasks, and speaks its replies.

Building this project provided practical experience with the complete speech pipeline:

* Microphone capture
* Ambient-noise calibration
* Online speech recognition
* Error handling
* Offline text-to-speech
* Rule-based command processing

The security requirement shaped the design meaningfully. Because voice input can never be trusted as a system command, the assistant executes only whitelisted actions. This demonstrates an important principle for voice- or text-driven automation.

The project also clarified where the **AI component** lives in such systems — speech recognition — and where simple deterministic logic, such as command rules, can be the better engineering choice.
