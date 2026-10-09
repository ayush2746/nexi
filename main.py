import ctypes
import datetime as dt
import os
import random
import smtplib
import sys
import urllib.parse
import webbrowser
from email.message import EmailMessage
from pathlib import Path

import pyautogui
import pyjokes
import pyttsx3
import speech_recognition as sr
import wikipedia
from deep_translator import GoogleTranslator
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QMovie

# Nexi voice assistant - Windows / Python 3.12
BASE_DIR = Path(__file__).resolve().parent
NOTES_FILE = BASE_DIR / "jarvis.txt"
GIF_FILE = BASE_DIR / "b.gif"

# Email credentials must be configured as environment variables.
EMAIL_ADDRESS = os.getenv("NEXI_EMAIL_ADDRESS", "")
EMAIL_APP_PASSWORD = os.getenv("NEXI_EMAIL_APP_PASSWORD", "")

# Initialize Windows SAPI text-to-speech, with a safe fallback voice choice.
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
if voices:
    # Prefer the second installed voice when available; otherwise use the first.
    engine.setProperty("voice", voices[1 if len(voices) > 1 else 0].id)
engine.setProperty("rate", 140)


def speak(text: str) -> None:
    """Speak text through Windows text-to-speech."""
    print(f"Nexi: {text}")
    engine.say(str(text))
    engine.runAndWait()


def wish() -> None:
    hour = dt.datetime.now().hour
    if hour < 12:
        speak("Good morning! How may I help you?")
    elif hour < 18:
        speak("Good afternoon! How may I help you?")
    else:
        speak("Good evening! How may I help you?")


def send_email(to_address: str, content: str) -> None:
    """Send an email using a Gmail App Password stored in environment variables."""
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        raise RuntimeError(
            "Email is not configured. Set NEXI_EMAIL_ADDRESS and "
            "NEXI_EMAIL_APP_PASSWORD environment variables first."
        )

    message = EmailMessage()
    message["Subject"] = "Nexi Assistant Message"
    message["From"] = EMAIL_ADDRESS
    message["To"] = to_address
    message.set_content(content)

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(message)


class AssistantThread(QThread):
    update_text_signal = pyqtSignal(str)

    LANGUAGE_CODES = {
        "English": "en-US",
        "Hindi": "hi-IN",
    }

    def __init__(self, selected_language: str):
        super().__init__()
        self.selected_language = selected_language
        self._running = True
        self._recognizer = sr.Recognizer()

    def stop(self) -> None:
        self._running = False

    def log(self, text: str) -> None:
        self.update_text_signal.emit(text)

    def listen_once(self) -> str:
        language_code = self.LANGUAGE_CODES.get(self.selected_language, "en-US")
        try:
            with sr.Microphone() as source:
                self.log("Listening...")
                self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=8)
            spoken_text = self._recognizer.recognize_google(audio, language=language_code)
            self.log(f"You said: {spoken_text}")

            # Commands are handled in English. Translate Hindi/other recognized speech.
            if self.selected_language != "English":
                try:
                    translated = GoogleTranslator(source="auto", target="en").translate(spoken_text)
                    self.log(f"Translated: {translated}")
                    return translated.lower()
                except Exception as exc:
                    self.log(f"Translation error: {exc}")
                    speak("I could not translate that. Please try again.")
                    return ""
            return spoken_text.lower()
        except sr.WaitTimeoutError:
            self.log("No speech detected. Listening again...")
        except sr.UnknownValueError:
            self.log("Sorry, I could not understand the speech.")
            speak("Sorry, say that again please.")
        except sr.RequestError as exc:
            self.log(f"Speech recognition service error: {exc}")
            speak("Speech recognition is temporarily unavailable.")
        except OSError as exc:
            self.log(f"Microphone error: {exc}")
            speak("I could not access the microphone. Check your microphone settings.")
        except Exception as exc:
            self.log(f"Listening error: {exc}")
        return ""

    def open_drive_or_folder(self, query: str) -> None:
        home = Path.home()
        destinations = {
            "open c drive": Path("C:\\"),
            "c drive": Path("C:\\"),
            "open d drive": Path("D:\\"),
            "d drive": Path("D:\\"),
            "open documents": home / "Documents",
            "documents": home / "Documents",
            "open desktop": home / "Desktop",
            "desktop": home / "Desktop",
            "open downloads": home / "Downloads",
            "downloads": home / "Downloads",
        }
        for phrase, path in destinations.items():
            if phrase in query:
                if path.exists():
                    os.startfile(str(path))
                    speak(f"Opening {phrase.replace('open ', '')}")
                else:
                    speak(f"I could not find {path}")
                return
        speak("I cannot recognize that drive or folder.")

    def close_application(self, app_name: str) -> None:
        # Only allow known process names to avoid executing arbitrary commands.
        processes = {
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "browser": "chrome.exe",
            "firefox": "firefox.exe",
            "mozilla firefox": "firefox.exe",
            "edge": "msedge.exe",
            "microsoft edge": "msedge.exe",
            "notepad": "notepad.exe",
            "calculator": "CalculatorApp.exe",
        }
        process = processes.get(app_name.strip().lower())
        if not process:
            speak("I can close Chrome, Firefox, Edge, Notepad, or Calculator by voice.")
            return
        result = os.system(f'taskkill /im "{process}"')
        if result == 0:
            speak(f"Closed {app_name}.")
        else:
            speak(f"I could not close {app_name}. It may not be running.")

    def handle_command(self, query: str) -> bool:
        """Handle one command. Return False to stop the assistant."""
        if not query:
            return True

        if any(word in query for word in ("goodbye", "exit assistant", "quit assistant")):
            speak("Goodbye, have a nice day!")
            return False

        if "open chatgpt" in query or "open chart gpt" in query:
            webbrowser.open("https://chatgpt.com/")
            speak("Opening ChatGPT")

        elif "search on youtube" in query:
            search_text = query.replace("search on youtube", "", 1).strip()
            if search_text:
                url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(search_text)
                webbrowser.open(url)
                speak(f"Searching YouTube for {search_text}")
            else:
                speak("Please say what you want to search for.")

        elif "open youtube" in query or query.strip() == "youtube" or "go to youtube" in query:
            webbrowser.open("https://www.youtube.com/")
            speak("Opening YouTube")

        elif "open google" in query or query.strip() == "google" or "go to google" in query:
            webbrowser.open("https://www.google.com/")
            speak("Opening Google")

        elif "play music" in query:
            speak("Playing music")
            video = random.choice([
                "https://www.youtube.com/watch?v=yZomIAahIZc",
                "https://www.youtube.com/watch?v=RpZzSH3nMdg",
            ])
            webbrowser.open(video)

        elif query.startswith("close "):
            self.close_application(query.replace("close ", "", 1).strip())

        elif any(phrase in query for phrase in (
            "open c drive", "open d drive", "open downloads", "open documents",
            "open desktop", "open drive", "c drive", "d drive"
        )):
            self.open_drive_or_folder(query)

        elif query.startswith("translate "):
            text_to_translate = query.replace("translate ", "", 1).strip()
            if text_to_translate:
                try:
                    translated = GoogleTranslator(source="auto", target="en").translate(text_to_translate)
                    self.log(f"Translated: {translated}")
                    speak(translated)
                except Exception as exc:
                    self.log(f"Translation error: {exc}")
                    speak("Sorry, I could not translate that.")

        elif "who made you" in query:
            speak("I was developed by a team.")

        elif "lock window" in query or "lock computer" in query:
            speak("Locking the device")
            ctypes.windll.user32.LockWorkStation()

        elif query in ("shutdown", "shut down", "shutdown the pc", "shut down the pc"):
            speak("Shutting down the computer in 10 seconds. Say cancel shutdown to cancel.")
            os.system("shutdown /s /t 10")

        elif "cancel shutdown" in query:
            os.system("shutdown /a")
            speak("Shutdown cancelled.")

        elif "restart computer" in query or query == "restart":
            speak("Restarting the computer in 10 seconds.")
            os.system("shutdown /r /t 10")

        elif query in ("hibernate", "hibernate computer"):
            speak("Hibernating the computer.")
            os.system("shutdown /h")

        elif "open stackoverflow" in query:
            webbrowser.open("https://stackoverflow.com/")
            speak("Opening Stack Overflow. Happy coding.")

        elif query == "time" or "what time" in query:
            speak("The time is " + dt.datetime.now().strftime("%I:%M %p"))

        elif query == "date" or "today's date" in query or "todays date" in query:
            speak("Today's date is " + dt.datetime.now().strftime("%d %B %Y"))

        elif query.startswith("open "):
            app_name = query.replace("open ", "", 1).strip()
            if app_name:
                speak(f"Opening {app_name}")
                # Windows search is used for app names that are not special cases above.
                pyautogui.hotkey("win")
                pyautogui.sleep(0.4)
                pyautogui.write(app_name, interval=0.05)
                pyautogui.press("enter")
            else:
                speak("What do you want me to open?")

        elif "who am i" in query or "who i am" in query:
            speak("If you're talking, you're definitely human!")

        elif "i love you" in query:
            speak("That's very kind of you!")

        elif "i hate you" in query:
            speak("I'll try to do better.")

        elif "go to hell" in query:
            speak("Let's keep things friendly.")

        elif "wikipedia" in query:
            topic = query.replace("wikipedia", "", 1).strip()
            if not topic:
                speak("Please tell me the topic to look up.")
            else:
                try:
                    result = wikipedia.summary(topic, sentences=3, auto_suggest=True)
                    self.log(result)
                    speak("According to Wikipedia")
                    speak(result)
                except Exception as exc:
                    self.log(f"Wikipedia error: {exc}")
                    speak("I could not find a Wikipedia summary for that topic.")

        elif "how are you" in query:
            speak("I am fine, thank you. How are you?")

        elif "joke" in query:
            speak(pyjokes.get_joke())

        elif query.startswith("write a note "):
            note = query.replace("write a note ", "", 1).strip()
            if note:
                timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with NOTES_FILE.open("a", encoding="utf-8") as file:
                    file.write(f"[{timestamp}] {note}\n")
                speak("I saved your note.")
            else:
                speak("Please say the note after 'write a note'.")

        elif "show note" in query or "display note" in query:
            if NOTES_FILE.exists():
                notes = NOTES_FILE.read_text(encoding="utf-8").strip()
                self.log(notes or "Your notes file is empty.")
                speak("I have displayed your notes.")
            else:
                speak("You do not have any saved notes yet.")

        elif "search on google" in query or query.startswith("search "):
            search_text = query.replace("search on google", "", 1).replace("search", "", 1).strip()
            if search_text:
                webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(search_text))
                speak(f"Searching Google for {search_text}")
            else:
                speak("Please tell me what to search for.")

        elif "send email" in query or query == "email" or query == "send mail":
            speak("Email sending needs recipient and message details in the code configuration.")
            self.log("Configure NEXI_EMAIL_ADDRESS and NEXI_EMAIL_APP_PASSWORD before using email.")
            # Intentionally do not send the hard-coded sample email from the original code.

        elif query in ("press space", "space"):
            pyautogui.press("space")
            speak("Pressed space.")

        elif query in ("press enter", "enter"):
            pyautogui.press("enter")
            speak("Pressed enter.")

        elif query in ("backspace", "press backspace", "delete"):
            pyautogui.press("backspace")
            speak("Pressed backspace.")

        elif query in ("tab", "press tab"):
            pyautogui.press("tab")
            speak("Pressed tab.")

        elif "alt tab" in query or "next page" in query or "go to next page" in query:
            pyautogui.hotkey("alt", "tab")
            speak("Switched window.")

        elif "caps lock" in query:
            pyautogui.press("capslock")
            speak("Toggled Caps Lock.")

        elif "start transcription" in query or "start recording" in query:
            speak("I am already listening for commands.")

        else:
            speak("Sorry, I do not know that command yet.")
        return True

    def run(self) -> None:
        wish()
        while self._running:
            query = self.listen_once()
            if not self.handle_command(query):
                self._running = False
                break


class ListeningApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexi Voice Assistant")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #000000; color: white;")

        layout = QtWidgets.QVBoxLayout(self)

        self.language_combobox = QtWidgets.QComboBox()
        self.language_combobox.addItems(["English", "Hindi"])
        self.language_combobox.setFixedWidth(220)
        self.language_combobox.setStyleSheet(
            "font-size: 18px; background-color: #36354E; color: white; "
            "border-radius: 8px; padding: 8px;"
        )
        language_row = QtWidgets.QHBoxLayout()
        language_row.addStretch()
        language_row.addWidget(QtWidgets.QLabel("Speech language:"))
        language_row.addWidget(self.language_combobox)
        layout.addLayout(language_row)

        self.gif_label = QtWidgets.QLabel()
        self.movie = None
        if GIF_FILE.exists():
            self.movie = QMovie(str(GIF_FILE))
            if self.movie.isValid():
                self.gif_label.setMovie(self.movie)
                self.movie.start()
            else:
                self.gif_label.setText("NEXI")
        else:
            self.gif_label.setText("NEXI\nAdd b.gif beside main.py to show your animation.")
        self.gif_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.gif_label, stretch=1)

        self.speech_display = QtWidgets.QTextEdit()
        self.speech_display.setReadOnly(True)
        self.speech_display.setMinimumHeight(160)
        self.speech_display.setStyleSheet(
            "font-size: 16px; background-color: #36354E; color: white; "
            "border-radius: 10px; padding: 10px;"
        )
        layout.addWidget(self.speech_display)

        self.assistant_thread = AssistantThread(self.language_combobox.currentText())
        self.assistant_thread.update_text_signal.connect(self.update_text)
        self.language_combobox.currentTextChanged.connect(self.update_language)
        self.assistant_thread.start()

    @QtCore.pyqtSlot(str)
    def update_text(self, text: str) -> None:
        self.speech_display.append(text)

    @QtCore.pyqtSlot(str)
    def update_language(self, language: str) -> None:
        self.assistant_thread.selected_language = language

    def closeEvent(self, event) -> None:
        self.assistant_thread.stop()
        if self.assistant_thread.isRunning():
            self.assistant_thread.wait(1500)
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ListeningApp()
    window.show()
    sys.exit(app.exec_())
