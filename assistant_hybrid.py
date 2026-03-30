# assistant_hybrid.py - Using Windows Built-in Speech 
import speech_recognition as sr
import datetime
import sys
import webbrowser
import pywhatkit
import pyjokes
import random
import requests
import os
import subprocess
import threading
import time

# Try Windows speech first
try:
    import win32com.client
    SPEECH_ENGINE = "windows"
    print("Using Windows Speech Engine")
except:
    try:
        import pyttsx3
        SPEECH_ENGINE = "pyttsx3"
        print("Using pyttsx3 Speech Engine")
    except:
        SPEECH_ENGINE = None
        print("No speech engine found")

class HybridAssistant:
    def __init__(self):
        print("\n" + "=" * 60)
        print("🎤 VOICE ASSISTANT")
        print("=" * 60)
        
        # Initialize speech recognition
        print("\n🔧 Setting up microphone...")
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            with self.microphone as source:
                print("   Adjusting for background noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone ready!")
            self.mic_available = True
            
        except Exception as e:
            print(f"⚠️ Microphone not available: {e}")
            self.mic_available = False
        
        # Initialize speech engine
        print("\n🔊 Setting up speech engine...")
        self.speech_engine = None
        
        if SPEECH_ENGINE == "windows":
            try:
                self.speech_engine = win32com.client.Dispatch("SAPI.SpVoice")
                self.speech_engine.Rate = 2  # Speed: -10 to 10
                self.speech_engine.Volume = 100
                print("✅ Windows Speech ready!")
                # Test speech
                self.speak("Voice assistant is ready!")
            except Exception as e:
                print(f"❌ Windows Speech error: {e}")
                self.speech_engine = None
                
        elif SPEECH_ENGINE == "pyttsx3":
            try:
                import pyttsx3
                self.speech_engine = pyttsx3.init()
                voices = self.speech_engine.getProperty('voices')
                if len(voices) > 1:
                    self.speech_engine.setProperty('voice', voices[1].id)
                self.speech_engine.setProperty('rate', 180)
                self.speech_engine.setProperty('volume', 1.0)
                print("✅ pyttsx3 Speech ready!")
                self.speak("Voice assistant is ready!")
            except Exception as e:
                print(f"❌ pyttsx3 error: {e}")
                self.speech_engine = None
        
        if self.speech_engine is None:
            print("⚠️ No speech engine available. Text only mode.")
        
        # Groq API
        self.groq_api_key = "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"
        self.ai_available = self.test_groq_api()
        
        if self.ai_available:
            print("✅ Groq AI ready!")
        else:
            print("⚠️ Groq AI not available")
        
        # Assistant info
        self.creator_name = "Krish Kukal"
        self.institute = "Tecnia Institute"
        self.mode = "voice"
        
        # Flag for shutdown/restart cancellation
        self.cancel_action = False
        
        # Mode switching phrases
        self.text_mode_phrases = ['text mode', 'switch to text', 'typing mode', 'text', 'typing']
        self.voice_mode_phrases = ['voice mode', 'switch to voice', 'speak mode', 'voice', 'speak']
        
        # Shutdown phrases
        self.shutdown_phrases = [
            'shutdown', 'shut down', 'shutdown pc', 'shut down pc', 
            'shutdown computer', 'turn off computer', 'turn off pc',
            'power off', 'shutdown system', 'shutdown my computer'
        ]
        
        # Restart phrases
        self.restart_phrases = [
            'restart', 'restart pc', 'restart computer', 'reboot',
            'reboot pc', 'reboot computer', 'restart system'
        ]
        
        # Cancel phrases
        self.cancel_phrases = [
            'cancel', 'cancel shutdown', 'cancel restart', 'stop shutdown',
            'don\'t shutdown', 'dont shutdown', 'abort shutdown', 'stop'
        ]
        
        # Greetings
        self.greetings = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! Good to hear from you. How can I assist?"
        ]
        
        # Creator phrases
        self.creator_phrases = [
            'who made you', 'who created you', 'who built you', 'who is your creator',
            'made by', 'created by'
        ]
        
        # Applications
        self.apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'chrome': 'chrome.exe',
            'control panel': 'control.exe',
            'controlpanel': 'control.exe',
        }
        
        # Folders
        self.folders = {
            'desktop': os.path.expanduser("~/Desktop"),
            'downloads': os.path.expanduser("~/Downloads"),
            'documents': os.path.expanduser("~/Documents"),
        }
        
        print("\n✅ ASSISTANT READY!")
        print("=" * 60)
    
    def speak(self, text):
        """SPEAK using Windows speech - GUARANTEED"""
        if not text:
            return
        
        # Always print what we're speaking
        print(f"\n🔊 Assistant: {text}")
        
        # Try to speak
        if self.speech_engine:
            try:
                if SPEECH_ENGINE == "windows":
                    self.speech_engine.Speak(text)
                else:
                    self.speech_engine.say(text)
                    self.speech_engine.runAndWait()
                return True
            except Exception as e:
                print(f"   Speech error: {e}")
        else:
            print("   (Speech not available - text only)")
        
        return False
    
    def listen_during_countdown(self):
        """Listen for cancellation during countdown"""
        try:
            if not self.mic_available:
                return None
            
            with self.microphone as source:
                print("\n🎤 Listening for cancellation... (say 'cancel')")
                # Short timeout for listening
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=2)
                text = self.recognizer.recognize_google(audio)
                print(f"📝 Detected: {text}")
                return text.lower()
        except:
            return None
    
    def listen_text_cancellation(self):
        """Listen for text input cancellation"""
        print("\n📝 Type 'cancel' to cancel or press Enter to continue...")
        import sys
        import select
        
        # Non-blocking input check
        if sys.platform == 'win32':
            import msvcrt
            if msvcrt.kbhit():
                response = input().strip().lower()
                return response
        return None
    
    def shutdown_computer(self):
        """Shutdown the computer with cancellation option"""
        self.cancel_action = False
        
        # Ask for confirmation first
        self.speak("Are you sure you want to shutdown the computer? Say yes to confirm.")
        
        # Listen for confirmation
        if self.mode == "voice":
            confirm = self.listen_voice()
        else:
            confirm = self.get_text_input()
        
        if confirm and ('yes' in confirm or 'confirm' in confirm or 'ok' in confirm):
            self.speak("Shutting down in 10 seconds. Say 'cancel' or type 'cancel' to stop.")
            print("\n⚠️ Shutting down in 10 seconds...")
            print("   Say 'cancel' or type 'cancel' to abort!")
            
            # Countdown with listening
            for i in range(10, 0, -1):
                print(f"   {i} seconds remaining... (say 'cancel' to abort)")
                
                # Check for voice cancellation
                if self.mode == "voice" and self.mic_available:
                    try:
                        with self.microphone as source:
                            # Quick listen for cancellation
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                            text = self.recognizer.recognize_google(audio).lower()
                            if any(cancel in text for cancel in ['cancel', 'stop', 'abort']):
                                self.speak("Shutdown cancelled.")
                                print("✅ Shutdown cancelled!")
                                return False
                    except:
                        pass
                
                # Check for text cancellation (if in text mode)
                if self.mode == "text":
                    # Check if user typed something
                    import msvcrt
                    if msvcrt.kbhit():
                        response = input().strip().lower()
                        if 'cancel' in response or 'stop' in response:
                            self.speak("Shutdown cancelled.")
                            print("✅ Shutdown cancelled!")
                            return False
                
                time.sleep(1)
            
            # Execute shutdown
            self.speak("Shutting down now.")
            print("💻 Shutting down...")
            os.system("shutdown /s /t 0")
            return True
        else:
            self.speak("Shutdown cancelled.")
            print("✅ Shutdown cancelled.")
            return False
    
    def restart_computer(self):
        """Restart the computer with cancellation option"""
        self.cancel_action = False
        
        # Ask for confirmation first
        self.speak("Are you sure you want to restart the computer? Say yes to confirm.")
        
        # Listen for confirmation
        if self.mode == "voice":
            confirm = self.listen_voice()
        else:
            confirm = self.get_text_input()
        
        if confirm and ('yes' in confirm or 'confirm' in confirm or 'ok' in confirm):
            self.speak("Restarting in 10 seconds. Say 'cancel' or type 'cancel' to stop.")
            print("\n⚠️ Restarting in 10 seconds...")
            print("   Say 'cancel' or type 'cancel' to abort!")
            
            # Countdown with listening
            for i in range(10, 0, -1):
                print(f"   {i} seconds remaining... (say 'cancel' to abort)")
                
                # Check for voice cancellation
                if self.mode == "voice" and self.mic_available:
                    try:
                        with self.microphone as source:
                            # Quick listen for cancellation
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                            text = self.recognizer.recognize_google(audio).lower()
                            if any(cancel in text for cancel in ['cancel', 'stop', 'abort']):
                                self.speak("Restart cancelled.")
                                print("✅ Restart cancelled!")
                                return False
                    except:
                        pass
                
                # Check for text cancellation (if in text mode)
                if self.mode == "text":
                    # Check if user typed something
                    import msvcrt
                    if msvcrt.kbhit():
                        response = input().strip().lower()
                        if 'cancel' in response or 'stop' in response:
                            self.speak("Restart cancelled.")
                            print("✅ Restart cancelled!")
                            return False
                
                time.sleep(1)
            
            # Execute restart
            self.speak("Restarting now.")
            print("💻 Restarting...")
            os.system("shutdown /r /t 0")
            return True
        else:
            self.speak("Restart cancelled.")
            print("✅ Restart cancelled.")
            return False
    
    def test_groq_api(self):
        """Test Groq API connection"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            response = requests.post(url, headers=headers, json=data, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def ask_groq(self, question):
        """Get answer from Groq AI"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant. Give short, direct answers (1-2 sentences)."},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            print("   🤔 Contacting Groq AI...")
            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                return answer
            return None
        except Exception as e:
            print(f"   Error: {e}")
            return None
    
    def listen_voice(self):
        """Listen for voice input"""
        if not self.mic_available:
            return None
        
        try:
            with self.microphone as source:
                print("\n🎤 Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            text = self.recognizer.recognize_google(audio)
            print(f"📝 You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_text_input(self):
        """Get text input"""
        return input("\n📝 You: ").strip().lower()
    
    def is_text_mode_switch(self, command):
        return any(phrase in command for phrase in self.text_mode_phrases)
    
    def is_voice_mode_switch(self, command):
        return any(phrase in command for phrase in self.voice_mode_phrases)
    
    def is_creator_question(self, command):
        return any(phrase in command for phrase in self.creator_phrases)
    
    def is_shutdown_command(self, command):
        """Check if command is asking to shutdown"""
        return any(phrase in command for phrase in self.shutdown_phrases)
    
    def is_restart_command(self, command):
        """Check if command is asking to restart"""
        return any(phrase in command for phrase in self.restart_phrases)
    
    def is_cancel_command(self, command):
        """Check if command is asking to cancel"""
        return any(phrase in command for phrase in self.cancel_phrases)
    
    def handle_open_command(self, command):
        """Open applications/websites"""
        to_open = command.replace('open', '').strip()
        
        if not to_open:
            self.speak("What would you like to open?")
            return False
        
        for app in self.apps:
            if app in to_open:
                try:
                    subprocess.Popen(self.apps[app])
                    self.speak(f"Opening {app}")
                    return True
                except:
                    pass
        
        for folder in self.folders:
            if folder in to_open:
                try:
                    os.startfile(self.folders[folder])
                    self.speak(f"Opening {folder} folder")
                    return True
                except:
                    pass
        
        try:
            webbrowser.open(f"https://www.{to_open}.com")
            self.speak(f"Opening {to_open}")
            return True
        except:
            pass
        
        self.speak(f"Sorry, I couldn't find {to_open}")
        return False
    
    def show_help(self):
        """Show help menu"""
        help_text = """
╔══════════════════════════════════════════════════════════════════════╗
║  VOICE ASSISTANT COMMANDS                                            ║
╠══════════════════════════════════════════════════════════════════════╣
║  BASIC COMMANDS:                                                     ║
║  • "time"           - Current time                                  ║
║  • "date"           - Current date                                  ║
║  • "joke"           - Tell a joke                                   ║
║  • "hello"          - Greeting                                      ║
║  • "who made you"   - About my creator (Krish Kukal from Tecnia)   ║
║                                                                      ║
║  SYSTEM COMMANDS:                                                    ║
║  • "shutdown"       - Shutdown computer (confirmation + 10 sec)    ║
║  • "restart"        - Restart computer (confirmation + 10 sec)     ║
║  • "cancel"         - Cancel shutdown/restart during countdown     ║
║                                                                      ║
║  OPEN COMMANDS:                                                      ║
║  • "open notepad"   - Open Notepad                                  ║
║  • "open calculator"- Open Calculator                               ║
║  • "open paint"     - Open Paint                                    ║
║  • "open control panel" - Open Control Panel                        ║
║  • "open chrome"    - Open Chrome browser                           ║
║  • "open google"    - Open Google website                           ║
║  • "play [song]"    - Play song on YouTube                          ║
║                                                                      ║
║  MODE SWITCHING:                                                     ║
║  • "text mode"      - Switch to typing                              ║
║  • "voice mode"     - Switch to speaking                            ║
║                                                                      ║
║  • "help"           - Show this menu                                ║
║  • "exit"           - Quit assistant                                ║
║                                                                      ║
║  💡 ASK ANY QUESTION - Groq AI will answer!                         ║
╚══════════════════════════════════════════════════════════════════════╝
        """
        print(help_text)
        self.speak("Here are the available commands")
    
    def process_command(self, command):
        """Process command and SPEAK the answer"""
        if not command:
            return True, False
        
        # Cancel command - if during countdown, this will be caught in the countdown loop
        # But also handle immediate cancel if someone says cancel before countdown
        if self.is_cancel_command(command):
            self.cancel_action = True
            self.speak("Cancelling action.")
            return True, False
        
        # Shutdown command
        if self.is_shutdown_command(command):
            self.shutdown_computer()
            return True, False
        
        # Restart command
        if self.is_restart_command(command):
            self.restart_computer()
            return True, False
        
        # Mode switching
        if self.is_text_mode_switch(command):
            if self.mode != "text":
                self.mode = "text"
                self.speak("Switched to text mode. Please type your commands.")
                return True, True
            return True, False
        
        if self.is_voice_mode_switch(command):
            if self.mic_available and self.mode != "voice":
                self.mode = "voice"
                self.speak("Switched to voice mode. Please speak your commands.")
                return True, True
            return True, False
        
        # Creator question
        if self.is_creator_question(command):
            self.speak(f"I was created by {self.creator_name} from {self.institute}!")
            return True, False
        
        # Open command
        if command.startswith('open '):
            self.handle_open_command(command)
            return True, False
        
        # Time
        if command in ['time', 'what time is it']:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {now}")
            return True, False
        
        # Date
        if command in ['date', 'what is the date']:
            today = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {today}")
            return True, False
        
        # Joke
        if command in ['joke', 'tell me a joke']:
            self.speak(pyjokes.get_joke())
            return True, False
        
        # Hello
        if any(word in command for word in ['hello', 'hi', 'hey']):
            self.speak(random.choice(self.greetings))
            return True, False
        
        # Play song
        if command.startswith('play '):
            song = command.replace('play', '').strip()
            if song:
                self.speak(f"Playing {song} on YouTube")
                pywhatkit.playonyt(song)
            return True, False
        
        # Search
        if command.startswith('search '):
            query = command.replace('search', '').strip()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                self.speak(f"Searching Google for {query}")
            return True, False
        
        # Help
        if command in ['help', 'commands']:
            self.show_help()
            return True, False
        
        # Exit
        if command in ['exit', 'quit', 'bye']:
            self.speak("Goodbye! Have a great day!")
            return False, False
        
        # AI Question - This will SPEAK the answer!
        if self.ai_available:
            print("   🤔 Asking Groq AI...")
            self.speak("Let me think about that...")
            
            response = self.ask_groq(command)
            
            if response:
                # THIS SPEAKS THE ANSWER
                self.speak(response)
            else:
                self.speak("Sorry, I couldn't get an answer from Groq AI.")
        else:
            self.speak("I didn't understand that. Say 'help' for commands.")
        
        return True, False
    
    def run(self):
        """Main loop"""
        # Initial greeting
        self.speak("Hello! I am your voice assistant.")
        
        # Mode selection
        print("\n" + "=" * 60)
        print("CHOOSE INPUT MODE:")
        print("=" * 60)
        
        if self.mic_available:
            print("1. Voice Mode (speak commands)")
            print("2. Text Mode (type commands)")
            print("=" * 60)
            
            while True:
                choice = input("\nSelect mode (1 or 2): ").strip()
                if choice == '1':
                    self.mode = "voice"
                    break
                elif choice == '2':
                    self.mode = "text"
                    break
                else:
                    print("Invalid choice. Enter 1 or 2.")
        else:
            self.mode = "text"
        
        # Mode confirmation
        if self.mode == "voice":
            self.speak("Voice mode activated. Speak your commands.")
        else:
            self.speak("Text mode activated. Type your commands.")
        
        self.show_help()
        
        print("\n" + "=" * 60)
        print("✅ Assistant is ready!")
        print("=" * 60)
        
        # Main loop
        while True:
            if self.mode == "voice":
                command = self.listen_voice()
                if command:
                    cont, _ = self.process_command(command)
                    if not cont:
                        break
            else:
                command = self.get_text_input()
                if command:
                    cont, _ = self.process_command(command)
                    if not cont:
                        break

if __name__ == "__main__":
    try:
        assistant = HybridAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n\n👋 Assistant stopped")
        try:
            assistant.speak("Goodbye!")
        except:
            pass
    except Exception as e:
        print(f"\n❌ Error: {e}")
