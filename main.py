import sys
from PyQt5.QtWidgets import QApplication

from memory_manager import MemoryManager
from desktop_controller import DesktopController
from browser_controller import BrowserController
from voice_input import VoiceInput
from command_parser import CommandParser
from task_executor import TaskExecutor
from gui_interface import AIWindow

class DesktopAICore:
    def __init__(self):
        self.memory = MemoryManager()
        self.desktop = DesktopController()
        self.browser = BrowserController()
        self.voice = VoiceInput()
        self.parser = CommandParser()
        self.executor = TaskExecutor(self.memory, self.desktop, self.browser, self.voice)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # Gives it a modern, clean look
    
    # Initialize Core Application Logic
    print("Initializing Core Components...")
    try:
        core = DesktopAICore()
    except Exception as e:
        print(f"Failed to initialize core components: {e}")
        sys.exit(1)
    
    # Initialize GUI
    window = AIWindow(core)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
