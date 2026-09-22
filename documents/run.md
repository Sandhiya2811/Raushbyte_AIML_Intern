# LEVEL 1

## task_2 

cd "C:\vs_code\Raushbyte_AIML_Intern\Level_1\Task_2\chatbot"

python chatbot.py

# lEVEL 2

## task_1
cd into Task_1
python src/face_detection.py

## task_2
cd into Task_2
python -m pip install -r requirements.txt
python src/voice_assistant.py

## task_3
cd into Task_3
python -m pip install -r requirements.txt
python src/automation_assistant.py

# git push command

cd "C:\vs_code\Raushbyte_AIML_Intern"
git init
git status
git add .
git commit -m "Add Level 1 Task 3 AI Presentation"
git push

# create virtual environ and activation
python -m venv .venv
.venv\Scripts\Activate.ps1

## 3. PowerShell Execution Policy Issue

If PowerShell blocks virtual environment activation, use one of the following options.

### Option A — Recommended

Allow locally created scripts for the current user only:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

### Option B — Use Command Prompt

Open **Command Prompt (CMD)** and run:

```cmd
.venv\Scripts\activate.bat
```