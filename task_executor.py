import os
import subprocess
from desktop_controller import DesktopController
from browser_controller import BrowserController
from memory_manager import MemoryManager
from voice_input import VoiceInput

class TaskExecutor:
    def __init__(self, memory: MemoryManager, desktop: DesktopController, browser: BrowserController, voice: VoiceInput):
        self.memory = memory
        self.desktop = desktop
        self.browser = browser
        self.voice = voice

    def execute(self, command_data: dict, original_text: str):
        action = command_data.get("action")
        params = command_data.get("parameters", {})
        
        print(f"Executing Action: {action} with params: {params}")
        status = "Success"
        
        try:
            if action == "open_application":
                self.voice.speak(f"Opening {params.get('app_name')}")
                success = self.desktop.open_application(params.get("app_name"))
                if not success: status = "Failed"
                
            elif action == "close_application":
                self.voice.speak("Closing application")
                self.desktop.close_application()
                
            elif action == "search_web":
                engine = params.get("engine", "google").lower()
                query = params.get("query", "")
                self.voice.speak(f"Searching {engine} for {query}")
                if engine == "youtube":
                    success = self.browser.search_youtube(query)
                else:
                    success = self.browser.search_google(query)
                if not success: status = "Failed"
                
            elif action == "open_website":
                url = params.get("url", "")
                self.voice.speak(f"Opening website {url}")
                success = self.browser.open_website(url)
                if not success: status = "Failed"
                
            elif action == "type_text":
                text = params.get("text", "")
                self.voice.speak("Typing text")
                self.desktop.type_text(text)
                
            elif action == "take_screenshot":
                filepath = self.desktop.take_screenshot()
                if filepath:
                    self.voice.speak("Screenshot taken.")
                else:
                    status = "Failed"
            
            elif action == "search_system":
                query = params.get("query", "")
                self.voice.speak(f"Searching your system for {query}")
                found_path = self.desktop.search_system_file(query)
                if found_path:
                    self.voice.speak("Found it. Opening now.")
                    # If it's a directory, force Windows Explorer to open it
                    if os.path.isdir(found_path):
                        subprocess.Popen(f'explorer "{found_path}"')
                    else:
                        # Use os.startfile on Windows to open the file with its default application
                        os.startfile(found_path)
                else:
                    self.voice.speak("I could not find a file or folder by that name.")
                    status = "Not Found"

            elif action == "create_folder":
                name = params.get("name", "New Folder")
                location = params.get("location", "Desktop")
                self.voice.speak(f"Creating folder {name} in {location}")
                path = self.desktop.create_folder(name, location)
                if path:
                    self.voice.speak("Folder created successfully.")
                else:
                    self.voice.speak("Failed to create folder.")
                    status = "Failed"
                    
            elif action == "create_file":
                name = params.get("name", "new_file.txt")
                location = params.get("location", "Desktop")
                self.voice.speak(f"Creating file {name} in {location}")
                path = self.desktop.create_file(name, location)
                if path:
                    self.voice.speak("File created successfully.")
                else:
                    self.voice.speak("Failed to create file.")
                    status = "Failed"
                    
            elif action == "generate_document":
                template_path = params.get("template_path", "template.docx")
                topic = params.get("topic", "")
                
                # Clean windows escaped paths that might come from the JSON parser
                template_path = template_path.replace("\\\\", "\\").strip()
                # Check if it was purely a fallback command without a path
                if "template.docx" in template_path and not os.path.exists(template_path):
                     # Try to use a default or find one
                     self.voice.speak(f"I need a valid template path to generate a document about {topic}.")
                     status = "Failed - No Template"
                else:
                    self.voice.speak(f"Generating a new document about {topic} based on your template.")
                    
                    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate_doc.py") if '__file__' in globals() else "generate_doc.py"
                    
                    try:
                        # Run the external script
                        result = subprocess.run(
                            ["python", script_path, template_path, topic],
                            capture_output=True, text=True
                        )
                        
                        if result.returncode == 0:
                            self.voice.speak("Document generated successfully.")
                        else:
                            print(f"Document Generation Error StdOut: {result.stdout}")
                            print(f"Document Generation Error StdErr: {result.stderr}")
                            self.voice.speak("There was an error generating the document.")
                            status = "Failed"
                    except Exception as ex:
                         print(f"Subprocess error: {ex}")
                         self.voice.speak("Failed to run document generation script.")
                         status = "Failed"
                    
            elif action == "create_ppt":
                import re
                topic = params.get("topic", "My Presentation")
                num_slides = int(params.get("num_slides", 5))
                location = params.get("location", "Desktop")

                # Build save path
                base_path = self.desktop._resolve_location(location)
                # Sanitise topic for use as filename
                safe_topic = re.sub(r'[\\/:*?"<>|]', '', topic).strip().replace(' ', '_')
                save_path = os.path.join(base_path, f"{safe_topic}.pptx")

                self.voice.speak(f"Creating a PowerPoint presentation about {topic} with {num_slides} slides.")

                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ppt_generator.py")
                try:
                    result = subprocess.run(
                        ["python", script_path, topic, str(num_slides), save_path],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        self.voice.speak(f"Done! Your presentation has been saved to {location} and is now opening.")
                    else:
                        print(f"PPT Error stdout: {result.stdout}")
                        print(f"PPT Error stderr: {result.stderr}")
                        self.voice.speak("There was an error creating the presentation.")
                        status = "Failed"
                except Exception as ex:
                    print(f"PPT subprocess error: {ex}")
                    self.voice.speak("Failed to run the presentation generator.")
                    status = "Failed"

            else:
                self.voice.speak("I am not sure how to do that.")
                status = "Unknown Action"
                
        except Exception as e:
            print(f"Execution error: {e}")
            status = f"Error: {e}"
            self.voice.speak("There was an error executing the command.")
            
        self.memory.add_to_history(original_text, action, status)
