import json
import os
from typing import List, Dict, Any

class MemoryManager:
    def __init__(self, memory_file: str = "memory.json"):
        self.memory_file = memory_file
        self.history: List[Dict[str, Any]] = []
        self.preferences: Dict[str, Any] = {}
        self.open_apps: List[str] = []
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.preferences = data.get('preferences', {})
                    self.open_apps = data.get('open_apps', [])
            except Exception as e:
                print(f"Error loading memory: {e}")

    def save_memory(self):
        try:
            with open(self.memory_file, 'w') as f:
                json.dump({
                    'history': self.history,
                    'preferences': self.preferences,
                    'open_apps': self.open_apps
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def add_to_history(self, command: str, action: str, status: str):
        self.history.append({
            'command': command,
            'action': action,
            'status': status
        })
        if len(self.history) > 100:  # Keep only last 100 commands
            self.history.pop(0)
        self.save_memory()

    def get_recent_commands(self) -> List[Dict[str, Any]]:
        return self.history[-10:]

    def set_preference(self, key: str, value: Any):
        self.preferences[key] = value
        self.save_memory()

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self.preferences.get(key, default)
        
    def add_open_app(self, app_name: str):
        if app_name not in self.open_apps:
            self.open_apps.append(app_name)
            self.save_memory()
            
    def remove_open_app(self, app_name: str):
        if app_name in self.open_apps:
            self.open_apps.remove(app_name)
            self.save_memory()
