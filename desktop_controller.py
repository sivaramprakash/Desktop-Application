import pyautogui
import subprocess
import os
import time
from typing import Optional
import glob

class DesktopController:
    def __init__(self):
        # PyAutoGUI failsafe and pause
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
    def open_application(self, app_name: str) -> bool:
        """Attempt to open an application by pressing Windows key, typing the name, and pressing Enter."""
        try:
            pyautogui.press('win')
            time.sleep(1)
            pyautogui.write(app_name)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2) # Wait for it to open
            return True
        except Exception as e:
            print(f"Error opening application {app_name}: {e}")
            return False

    def close_application(self, app_name: str = None) -> bool:
        """Close the currently active window (Alt+F4)."""
        try:
            pyautogui.hotkey('alt', 'f4')
            return True
        except Exception as e:
            print(f"Error closing application: {e}")
            return False

    def type_text(self, text: str):
        """Type given text."""
        pyautogui.write(text, interval=0.05)

    def press_key(self, key: str):
        """Press a specific key."""
        pyautogui.press(key)

    def hotkey(self, *keys):
        """Press a key combination."""
        pyautogui.hotkey(*keys)

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left'):
        """Click at current location or specified coordinates."""
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, button=button)
        else:
            pyautogui.click(button=button)

    def take_screenshot(self, filepath: str = "screenshot.png") -> str:
        """Take a screenshot and save it."""
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            return os.path.abspath(filepath)
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return ""

    def launch_system_tool(self, command: str) -> bool:
        """Launch system commands like explorer, calc, etc."""
        try:
            subprocess.Popen(command, shell=True)
            return True
        except Exception as e:
            print(f"Error launching command {command}: {e}")
            return False

    def search_system_file(self, query: str) -> Optional[str]:
        """
        Search for a file or folder on the local machine starting from the User Profile.
        Returns the first matched absolute path.
        """
        import os

        # Clean query
        clean_query = query.lower().replace(" folder", "").replace(" directory", "").replace(" file", "").strip()
        if clean_query.startswith("the "):
            clean_query = clean_query[4:]
            
        user_dir = os.path.expanduser("~")
        
        # Fast path for common user directories
        common_dirs = {
            "desktop": os.path.join(user_dir, "Desktop"),
            "documents": os.path.join(user_dir, "Documents"),
            "downloads": os.path.join(user_dir, "Downloads"),
            "pictures": os.path.join(user_dir, "Pictures"),
            "music": os.path.join(user_dir, "Music"),
            "videos": os.path.join(user_dir, "Videos")
        }
        
        if clean_query in common_dirs:
            if os.path.exists(common_dirs[clean_query]):
                print(f"Found standard directory: {common_dirs[clean_query]}")
                return common_dirs[clean_query]
                
        # If absolute path provided, return it
        if os.path.isabs(query) and os.path.exists(query):
            return query
            
        search_dirs = [
            os.path.join(user_dir, "Desktop"),
            os.path.join(user_dir, "Documents"),
            os.path.join(user_dir, "Downloads"),
            os.path.join(user_dir, "Pictures"),
            os.path.join(user_dir, "Music"),
            user_dir # fallback to root
        ]
        
        print(f"Searching for '{clean_query}' in common user directories...")
        
        ignore_dirs = {'AppData', 'appdata', '.git', 'node_modules', 'venv', '.venv', '__pycache__', '.idea', '.vscode'}
        searched_roots = set()
        
        for base_dir in search_dirs:
            if not os.path.exists(base_dir):
                 continue
            
            # Simple os.walk to find a match (case insensitive)
            for root, dirs, files in os.walk(base_dir):
                if root in searched_roots:
                    # Skip if we already searched this root (e.g. from a previous base_dir)
                    dirs[:] = []
                    continue
                searched_roots.add(root)
                
                # Filter out ignored directories in-place so os.walk doesn't traverse them
                dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
                
                # First pass: look for exact matches
                for d in dirs:
                    if clean_query == d.lower():
                        match = os.path.join(root, d)
                        print(f"Found exact folder: {match}")
                        return match
                for f in files:
                    if clean_query == f.lower() or clean_query == os.path.splitext(f)[0].lower():
                        match = os.path.join(root, f)
                        print(f"Found exact file: {match}")
                        return match
                        
                # Second pass: look for partial matches
                for d in dirs:
                    if clean_query in d.lower():
                        match = os.path.join(root, d)
                        print(f"Found partial folder: {match}")
                        return match
                for f in files:
                    if clean_query in f.lower():
                        match = os.path.join(root, f)
                        print(f"Found partial file: {match}")
                        return match
                        
        print(f"Could not find any file or folder matching '{clean_query}'.")
        return None

    def _resolve_location(self, location: str) -> str:
        """Helper to resolve 'Desktop', 'Downloads', etc. to absolute paths."""
        if not location:
            return os.path.expanduser("~")
            
        location_lower = location.lower().strip()
        user_dir = os.path.expanduser("~")
        common_dirs = {
            "desktop": os.path.join(user_dir, "Desktop"),
            "documents": os.path.join(user_dir, "Documents"),
            "downloads": os.path.join(user_dir, "Downloads"),
            "pictures": os.path.join(user_dir, "Pictures"),
            "music": os.path.join(user_dir, "Music"),
            "videos": os.path.join(user_dir, "Videos")
        }
        
        if location_lower in common_dirs:
            return common_dirs[location_lower]
        
        if os.path.isabs(location):
            return location
            
        # Default fallback is creating it in the user directory
        return user_dir

    def create_folder(self, name: str, location: str) -> Optional[str]:
        """Creates a new folder at the specified location."""
        try:
            base_path = self._resolve_location(location)
            full_path = os.path.join(base_path, name)
            
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                print(f"Created folder: {full_path}")
                return full_path
            else:
                print(f"Folder already exists: {full_path}")
                return full_path
        except Exception as e:
            print(f"Error creating folder {name} at {location}: {e}")
            return None

    def create_file(self, name: str, location: str, content: str = "") -> Optional[str]:
        """Creates a new file at the specified location."""
        try:
            base_path = self._resolve_location(location)
            full_path = os.path.join(base_path, name)
            
            # Create base directories if they don't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created file: {full_path}")
            return full_path
        except Exception as e:
            print(f"Error creating file {name} at {location}: {e}")
            return None
