import speech_recognition as sr
import pyttsx3
import traceback

class VoiceInput:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        # You can adjust voice properties here
        # voices = self.engine.getProperty('voices')
        # self.engine.setProperty('voice', voices[1].id) # typically female voice

    def speak(self, text: str):
        """Convert text to speech."""
        print(f"AI: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in TTS: {e}")

    def listen_for_wake_word(self, wake_words) -> bool:
        """Continuously listen in the background for the wake word.
        
        Args:
            wake_words: A string or list of strings. Any match triggers activation.
        """
        # Normalize to list so we can check multiple variants
        if isinstance(wake_words, str):
            wake_words = [wake_words]
        wake_words = [w.lower() for w in wake_words]

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Waiting for wake word...")
            try:
                audio = self.recognizer.listen(source, timeout=1)
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                for variant in wake_words:
                    if variant in text:
                        return True
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass  # Just loop again
            except Exception as e:
                pass
        return False

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """Listen for audio and convert to text."""
        with sr.Microphone() as source:
            print("Listening for command...")
            self.speaker_beep = True # optional sound cue
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                print("Processing speech...")
                text = self.recognizer.recognize_google(audio)
                print(f"User: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                print("Listening timed out.")
                return ""
            except sr.UnknownValueError:
                print("Could not understand audio.")
                return ""
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return ""
            except Exception as e:
                print(f"Error during listening: {e}")
                traceback.print_exc()
                return ""
