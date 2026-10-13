import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class CommandWorker(QThread):
    finished = pyqtSignal(dict, str)
    error = pyqtSignal(str)

    def __init__(self, parser, command_text):
        super().__init__()
        self.parser = parser
        self.command_text = command_text

    def run(self):
        try:
            parsed = self.parser.parse_command(self.command_text)
            self.finished.emit(parsed, self.command_text)
        except Exception as e:
            self.error.emit(str(e))

class WakeWordWorker(QThread):
    heard = pyqtSignal()
    
    def __init__(self, voice_input):
        super().__init__()
        self.voice_input = voice_input
        self.running = True

    # All common speech-to-text transcriptions of "hey luna"
    WAKE_VARIANTS = [
        "hey luna",
        "heyy luna",
        "hay luna",
        "hi luna",
        "hey lune",
        "hey loona",
        "hey lona",
        "luna"
    ]

    def run(self):
        while self.running:
            if self.voice_input.listen_for_wake_word(self.WAKE_VARIANTS):
                self.heard.emit()
                # Pause listening for wake word while handling the command
                break
                
    def stop(self):
        self.running = False

class VoiceWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, voice_input):
        super().__init__()
        self.voice_input = voice_input

    def run(self):
        try:
            text = self.voice_input.listen()
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))

class AIWindow(QWidget):
    def __init__(self, app_core):
        super().__init__()
        self.app_core = app_core
        self.init_ui()
        self.start_wake_word_listener()

    def start_wake_word_listener(self):
        self.wake_worker = WakeWordWorker(self.app_core.voice)
        self.wake_worker.heard.connect(self.on_wake_word_heard)
        self.wake_worker.start()

    def on_wake_word_heard(self):
        self.log("<span style='color: #4CAF50;'>AI:</span> Wake word heard. Listening for command...")
        self.app_core.voice.speak("Yes?")
        self.process_voice_command()

    def init_ui(self):
        self.setWindowTitle('Desktop AI Assistant')
        self.resize(500, 600)

        layout = QVBoxLayout()

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        # basic styling
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas; font-size: 13px;")
        layout.addWidget(QLabel("Activity Log:"))
        layout.addWidget(self.log_area)

        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type a command here (e.g., 'Open Chrome' or 'Search YouTube for Python')...")
        self.input_box.returnPressed.connect(self.process_text_command)
        self.input_box.setStyleSheet("padding: 8px; font-size: 14px;")
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.process_text_command)
        self.send_btn.setStyleSheet("padding: 8px; background-color: #0078D7; color: white; font-weight: bold;")

        self.mic_btn = QPushButton("🎤 Voice")
        self.mic_btn.clicked.connect(self.process_voice_command)
        self.mic_btn.setStyleSheet("padding: 8px; background-color: #d13438; color: white; font-weight: bold;")

        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_btn)
        input_layout.addWidget(self.mic_btn)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        self.log("System initialized. Waiting for commands...")
        self.app_core.voice.speak("Hello! I am Luna, your desktop assistant. Say hey Luna to activate me.")

    def log(self, text):
        self.log_area.append(text)

    def process_text_command(self):
        text = self.input_box.text().strip()
        if text:
            self.input_box.clear()
            self.log(f"<span style='color: #569cd6;'>User:</span> {text}")
            self.parse_and_execute(text)

    def process_voice_command(self):
        self.mic_btn.setEnabled(False)
        self.log("<span style='color: #4CAF50;'>AI:</span> Listening...")
        self.voice_worker = VoiceWorker(self.app_core.voice)
        self.voice_worker.finished.connect(self.on_voice_finished)
        self.voice_worker.error.connect(self.on_error)
        self.voice_worker.start()

    def on_voice_finished(self, text):
        self.mic_btn.setEnabled(True)
        if text:
            self.log(f"<span style='color: #569cd6;'>User (Voice):</span> {text}")
            self.parse_and_execute(text)
        else:
            self.log("<span style='color: #4CAF50;'>AI:</span> Could not hear anything.")
            
        # Restart wake word listener after a command finishes (or fails)
        self.start_wake_word_listener()

    def parse_and_execute(self, text):
        self.log("<span style='color: #4CAF50;'>AI:</span> Parsing command...")
        self.app_core.voice.speak("Got it, let me process that.")
        self.cmd_worker = CommandWorker(self.app_core.parser, text)
        self.cmd_worker.finished.connect(self.on_command_parsed)
        self.cmd_worker.error.connect(self.on_error)
        self.cmd_worker.start()

    def on_command_parsed(self, parsed_data, original_text):
        action = parsed_data.get('action')
        error = parsed_data.get('error')
        if error:
            self.log(f"<span style='color: #4CAF50;'>AI:</span> Could not parse command (Error: {error})")
            self.app_core.voice.speak("Sorry, I could not understand that command.")
            return
            
        # Friendly spoken action names
        action_phrases = {
            "open_application": "Opening application.",
            "close_application": "Closing application.",
            "search_web": "Searching the web.",
            "open_website": "Opening website.",
            "type_text": "Typing text.",
            "take_screenshot": "Taking a screenshot.",
            "search_system": "Searching your system.",
            "create_file": "Creating a file.",
            "create_folder": "Creating a folder.",
            "generate_document": "Generating a document.",
            "unknown": "Sorry, I don't know how to do that."
        }
        spoken = action_phrases.get(action, f"Understood. Performing {action}.")
        self.log(f"<span style='color: #4CAF50;'>AI:</span> Understood action -> {action}")
        if action == "unknown":
            self.app_core.voice.speak(spoken)
            return
        self.app_core.executor.execute(parsed_data, original_text)
        self.log("<span style='color: #4CAF50;'>AI:</span> Action executed.")

    def on_error(self, err):
        self.log(f"<span style='color: red;'>Error:</span> {err}")
        self.app_core.voice.speak("An error occurred. Please try again.")
        self.mic_btn.setEnabled(True)
