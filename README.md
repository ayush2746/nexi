# Nexi Voice Assistant

Nexi is a Windows desktop voice assistant built with Python and PyQt5. It listens for spoken commands, displays recognized speech in its window, and responds using Windows text-to-speech.

## Features

- Speech recognition in English and Hindi. Hindi speech is translated to English before commands are handled.
- Spoken responses and a desktop interface.
- Web searches and shortcuts for Google, YouTube, ChatGPT, and Stack Overflow.
- Wikipedia summaries, jokes, translation, and date and time.
- Windows app and folder shortcuts, keyboard actions, and computer power commands.
- Voice notes saved locally to `jarvis.txt`.
- Optional animated interface using a `b.gif` file placed beside `main.py`.

> **Caution:** Nexi can lock, shut down, restart, or hibernate the computer. Use those commands only when you intend to perform the action. A spoken shutdown can be cancelled by saying “cancel shutdown” before its countdown finishes.

## Requirements

- Windows
- Python 3.12 and the Python launcher (`py`)
- A working microphone and speakers
- An internet connection for online speech recognition, translation, and Wikipedia lookups

The dependencies are listed in [`requirements.txt`](./requirements.txt). The setup script creates a project-local `.venv` virtual environment and installs them there.

## Setup

1. Install Python 3.12 for Windows. During installation, enable the Python launcher.
2. Download or clone this project and open the `Nexi` project folder.
3. Double-click `setup.bat`, or run it from Command Prompt:

   ```bat
   setup.bat
   ```

   The script checks for Python 3.12, creates `.venv` if needed, upgrades pip, and installs the dependencies. Keep the computer connected to the internet while dependencies are installing.

4. If Windows asks for microphone access, allow it for the Python application.

## Run

After setup completes, double-click `run.bat`, or run:

```bat
run.bat
```

The assistant starts listening when its window opens. Choose **English** or **Hindi** from the language selector, speak a command, and use “goodbye,” “exit assistant,” or “quit assistant” to stop the listening loop before closing the window.

You can also start it directly with the virtual environment's Python:

```bat
.venv\Scripts\python.exe main.py
```

## Example commands

| Say | Result |
| --- | --- |
| “What time is it?” | Announces the current time |
| “Today’s date” | Announces the date |
| “Search for [topic]” | Opens Google search results |
| “Search on YouTube for [topic]” | Opens YouTube search results |
| “Wikipedia [topic]” | Reads a short Wikipedia summary |
| “Translate [text]” | Translates the text to English |
| “Tell me a joke” | Tells a joke |
| “Open YouTube” | Opens YouTube |
| “Open downloads” | Opens the Downloads folder |
| “Open [app name]” | Uses Windows search to open an app |
| “Close Chrome” | Attempts to close a supported app |
| “Write a note [text]” | Saves a timestamped note in `jarvis.txt` |
| “Show notes” | Displays saved notes in the window |
| “Lock computer” | Locks the Windows session |
| “Goodbye” | Stops the assistant’s listening loop |

Voice recognition and translation depend on online services and may not work without an internet connection. Commands are handled in English; Hindi speech is translated before command handling.

## Optional animation

Place a valid animated GIF named `b.gif` in the same folder as `main.py`. If the file is absent or invalid, the window displays a text fallback instead.

## Email status

The voice command currently does not send email; it only displays a configuration message. The source includes a separate email helper that expects `NEXI_EMAIL_ADDRESS` and `NEXI_EMAIL_APP_PASSWORD` environment variables, but configuring those variables alone does not enable email sending by voice.

## Troubleshooting

- **Python launcher or Python 3.12 not found:** Install Python 3.12 and enable the launcher, then run `setup.bat` again.
- **Setup or dependency installation fails:** Confirm that Python 3.12 and an internet connection are available. `PyAudio` installation can be platform-sensitive; read the installation error for the dependency that failed.
- **Microphone errors:** Check Windows microphone privacy permissions, confirm a microphone is connected and selected, and close other applications that may be using it.
- **No response or recognition errors:** Check the internet connection and microphone input level. Speech recognition uses an online service.
- **No animation:** Confirm the file is named `b.gif` and is beside `main.py`. The animation is optional.
- **Start-up errors:** Run `setup.bat` again to install the dependencies in `.venv`, then launch with `run.bat`.
