import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class CommandParser:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key and self.api_key.strip() != "your_openai_api_key_here":
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.client = None
        else:
            self.client = None
            print("Warning: OPENAI_API_KEY not found or invalid. Command parser will not work. Please add it to your .env file.")

    def parse_command(self, user_input: str) -> dict:
        """
        Parses natural language command into structured action.
        Returns a dictionary like:
        {
            "action": "open_application",
            "parameters": {"app_name": "chrome"}
        }
        """
        if not self.client:
            return {"action": "unknown", "parameters": {}, "error": "No API key"}

        system_prompt = """
        You are an AI assistant that controls a desktop computer.
        Your job is to parse the user's command into a JSON object indicating the action and parameters.
        Supported actions:
        1. "open_application" (parameters: "app_name" - e.g., "chrome", "vscode", "notepad")
        2. "close_application" (parameters: none)
        3. "search_web" (parameters: "query", "engine": "google" or "youtube")
        4. "open_website" (parameters: "url" - e.g., "https://web.whatsapp.com")
        5. "type_text" (parameters: "text")
        6. "click" (parameters: "x" (int), "y" (int) - optional)
        7. "take_screenshot" (parameters: none)
        8. "search_system" (parameters: "query" - what file or folder to find and open)
        9. "create_file" (parameters: "name", "location" - e.g., "Desktop", "Downloads", or specific path)
        10. "create_folder" (parameters: "name", "location" - e.g., "Desktop", "Downloads", or specific path)
        11. "generate_document" (parameters: "template_path", "topic")
        12. "create_ppt" (parameters: "topic", "num_slides" (int, default 5), "location" - e.g., "Desktop", "Downloads")
        13. "unknown" (when command is not supported)
        
        Provide your response as ONLY a valid JSON object. Do not use markdown syntax like ```json.
        Example: {"action": "generate_document", "parameters": {"template_path": "C:\\Users\\Documents\\template.docx", "topic": "AI in Healthcare"}}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.0
            )
            content = response.choices[0].message.content.strip()
            
            # Additional safety stripping just in case
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            return json.loads(content)
        except json.JSONDecodeError as decode_err:
            print(f"JSON Parsing Error: {decode_err} for content: {content}")
            return {"action": "unknown", "parameters": {}, "error": "Bad JSON"}
        except Exception as e:
            print(f"Error parsing command with AI: {e}")
            return self._fallback_parse(user_input)

    def _fallback_parse(self, original_input: str) -> dict:
        """Simple string-matching fallback if API fails."""
        user_input = original_input.lower()

        # --- PPT / Presentation ---
        ppt_keywords = ["ppt", "presentation", "powerpoint", "slides", "slide show"]
        trigger_keywords = ["create", "make", "generate", "build"]
        if any(k in user_input for k in ppt_keywords) and any(t in user_input for t in trigger_keywords):
            topic = "My Presentation"
            num_slides = 5
            location = "Desktop"

            # Extract topic after "about"
            if " about " in user_input:
                idx = user_input.index(" about ") + 7
                end_idx = len(original_input)
                for stop in [" with ", " on ", " in ", " for "]:
                    if stop in user_input[idx:]:
                        end_idx = idx + user_input[idx:].index(stop)
                        break
                topic = original_input[idx:end_idx].strip()

            # Extract topic after "on"
            elif " on " in user_input:
                idx = user_input.index(" on ") + 4
                end_idx = len(original_input)
                for stop in [" with ", " in ", " for "]:
                    if stop in user_input[idx:]:
                        end_idx = idx + user_input[idx:].index(stop)
                        break
                topic = original_input[idx:end_idx].strip()

            # Extract number of slides
            import re
            match = re.search(r'(\d+)\s*slides?', user_input)
            if match:
                num_slides = int(match.group(1))

            # Extract location
            if " on desktop" in user_input or " on my desktop" in user_input:
                location = "Desktop"
            elif " in downloads" in user_input:
                location = "Downloads"
            elif " in documents" in user_input:
                location = "Documents"

            return {"action": "create_ppt", "parameters": {"topic": topic, "num_slides": num_slides, "location": location}}

        if "generate" in user_input and "document" in user_input:
            topic = "General Topic"
            template_path = "template.docx"
            
            # Extract topic: "about X"
            if "about " in user_input:
                about_idx = user_input.index("about ") + 6
                end_idx = len(original_input)
                # If they say "about X based on Y"
                if " based on " in user_input[about_idx:]:
                    end_idx = about_idx + user_input[about_idx:].index(" based on ")
                elif ' "' in user_input[about_idx:]:
                     end_idx = about_idx + user_input[about_idx:].index(' "')
                topic = original_input[about_idx:end_idx].strip()
            
            # Extract template: "based on X" or from explicit quotes
            if " based on " in user_input:
                based_idx = user_input.index(" based on ") + 10
                path_str = original_input[based_idx:].strip()
                # Remove quotes if they wrapped it in them
                if path_str.startswith('"') and path_str.endswith('"'):
                    path_str = path_str[1:-1]
                if path_str.startswith("'") and path_str.endswith("'"):
                    path_str = path_str[1:-1]
                if path_str:
                    template_path = path_str.strip()
                    
            elif '"' in original_input:
                 # Just find the first quoted string as a fallback for the path
                 parts = original_input.split('"')
                 if len(parts) >= 3:
                     template_path = parts[1]
                
            return {"action": "generate_document", "parameters": {"template_path": template_path, "topic": topic}}
            
        if "open" in user_input and "chrome" in user_input:
            return {"action": "open_application", "parameters": {"app_name": "chrome"}}
        if "open" in user_input and "notepad" in user_input:
             return {"action": "open_application", "parameters": {"app_name": "notepad"}}
        if "close" in user_input:
            return {"action": "close_application", "parameters": {}}
        if "google" in user_input:
            query = user_input.replace("search google for", "").replace("search google", "").strip()
            return {"action": "search_web", "parameters": {"engine": "google", "query": query}}
        if "youtube" in user_input:
            if "channel" in user_input and "open" in user_input:
                 query = user_input.replace("open youtube channel", "").replace("for", "").strip()
                 # To open a channel, YouTube's search works best if we just pass the query. 
                 # We'll just search it for now, as knowing the exact `@handle` beforehand is hard.
                 return {"action": "search_web", "parameters": {"engine": "youtube", "query": query}}
                 
            query = user_input.replace("search youtube for", "").replace("search youtube", "").strip()
            return {"action": "search_web", "parameters": {"engine": "youtube", "query": query}}
        if "screenshot" in user_input:
            return {"action": "take_screenshot", "parameters": {}}
            
        if "folder" in user_input and ("create " in user_input or "make " in user_input):
            name = "New Folder"
            location = "Desktop"
            
            # Find original casing name
            if " named " in user_input:
                start_idx = user_input.index(" named ") + 7
                end_idx = len(user_input)
                if " on " in user_input[start_idx:]:
                    end_idx = start_idx + user_input[start_idx:].index(" on ")
                elif " in " in user_input[start_idx:]:
                    end_idx = start_idx + user_input[start_idx:].index(" in ")
                name_part = original_input[start_idx:end_idx].strip()
                if name_part: name = name_part
            
            if " on " in user_input:
                location = original_input[original_input.lower().rfind(" on ") + 4:].replace("my ", "").replace("My ", "").strip()
            elif " in " in user_input:
                location = original_input[original_input.lower().rfind(" in ") + 4:].replace("my ", "").replace("My ", "").strip()
                
            return {"action": "create_folder", "parameters": {"name": name, "location": location}}
            
        if "file" in user_input and ("create " in user_input or "make " in user_input):
            name = "new_file.txt"
            location = "Desktop"
            
            # Find original casing name
            if " named " in user_input:
                start_idx = user_input.index(" named ") + 7
                end_idx = len(user_input)
                if " on " in user_input[start_idx:]:
                    end_idx = start_idx + user_input[start_idx:].index(" on ")
                elif " in " in user_input[start_idx:]:
                    end_idx = start_idx + user_input[start_idx:].index(" in ")
                name_part = original_input[start_idx:end_idx].strip()
                if name_part: name = name_part
            elif " called " in user_input:
                start_idx = user_input.index(" called ") + 8
                end_idx = len(user_input)
                if " on " in user_input[start_idx:]:
                    end_idx = start_idx + user_input[start_idx:].index(" on ")
                elif " in " in user_input[start_idx:]:
                    end_idx = start_idx + user_input[start_idx:].index(" in ")
                name_part = original_input[start_idx:end_idx].strip()
                if name_part: name = name_part
            
            if " on " in user_input:
                location = original_input[original_input.lower().rfind(" on ") + 4:].replace("my ", "").replace("My ", "").strip()
            elif " in " in user_input:
                location = original_input[original_input.lower().rfind(" in ") + 4:].replace("my ", "").replace("My ", "").strip()
                
            return {"action": "create_file", "parameters": {"name": name, "location": location}}
        
        # More robust file/folder matching
        if "find" in user_input or "search my computer" in user_input:
            query = user_input.replace("find", "").replace("search my computer for", "").strip()
            return {"action": "search_system", "parameters": {"query": query}}
            
        if "open folder" in user_input:
            query = user_input.replace("open folder", "").strip()
            return {"action": "search_system", "parameters": {"query": query}}
            
        if "open file" in user_input:
            query = user_input.replace("open file", "").strip()
            return {"action": "search_system", "parameters": {"query": query}}
            
        # Catch-all for "open [something]" if it wasn't caught by chrome/notepad hooks above
        if "open" in user_input and len(user_input.split("open", 1)[1].strip()) > 0:
             query = user_input.split("open", 1)[1].strip()
             # Assume they want to search for it on system
             return {"action": "search_system", "parameters": {"query": query}}
        
        return {"action": "unknown", "parameters": {}, "error": "Fallback parser didn't understand. Could not use AI."}

