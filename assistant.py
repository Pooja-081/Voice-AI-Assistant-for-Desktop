

import os
import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import subprocess
import playsound
from gtts import gTTS
import requests
from bs4 import BeautifulSoup
import platform
import glob

def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        audio_file = "response.mp3"
        tts.save(audio_file)
        playsound.playsound(audio_file)
        os.remove(audio_file)
    except Exception as e:
        print(f"Error in speak function: {e}")
        # Fallback to pyttsx3 if gTTS fails
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except:
            print("Both TTS methods failed")

def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        print("Recognizing...")
        text = recognizer.recognize_google(audio).lower()
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Speech service error: {e}")
        return "Error: Speech service unavailable"
    except sr.WaitTimeoutError:
        print("Listening timeout")
        return ""
    except Exception as e:
        print(f"Error in listen function: {e}")
        return ""

def find_file(file_name):
    """Find file in common directories with various extensions"""
    # Common directories to search
    search_dirs = [
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads"),
        os.getcwd()  # Current directory
    ]
    
    # Common file extensions
    extensions = ['', '.txt', '.doc', '.docx', '.pdf', '.py', '.html', '.css', '.js']
    
    for directory in search_dirs:
        if not os.path.exists(directory):
            continue
            
        for ext in extensions:
            # Try exact match
            file_path = os.path.join(directory, f"{file_name}{ext}")
            if os.path.exists(file_path):
                return file_path
            
            # Try case-insensitive search
            pattern = os.path.join(directory, f"{file_name}{ext}")
            matches = glob.glob(pattern, recursive=False)
            if matches:
                return matches[0]  # Return first match
    
    return None

def open_file(file_name):
    """Open file with improved search and cross-platform compatibility"""
    file_path = find_file(file_name)
    
    if not file_path:
        return f"File '{file_name}' not found in common directories."
    
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
        
        return f"Opening {os.path.basename(file_path)}"
    except Exception as e:
        print(f"Error opening file: {e}")
        return f"Could not open {file_name}"

def search_file(file_name, keyword):
    """Search for keyword in file with better error handling"""
    file_path = find_file(file_name)
    
    if not file_path:
        return f"File '{file_name}' not found."
    
    try:
        # Try different encodings
        encodings = ['utf-8', 'utf-16', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as file:
                    content = file.read()
                    if keyword.lower() in content.lower():
                        return f"'{keyword}' found in {os.path.basename(file_path)}"
                    else:
                        return f"'{keyword}' not found in {os.path.basename(file_path)}"
            except UnicodeDecodeError:
                continue
        
        return f"Could not read {file_name} - unsupported file format"
    except Exception as e:
        print(f"Error searching file: {e}")
        return f"Error searching in {file_name}"

def google_search(query):
    try:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching Google for {query}"
    except Exception as e:
        print(f"Error opening Google search: {e}")
        return "Error opening Google search"

def youtube_search(query):
    try:
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"Searching YouTube for {query}"
    except Exception as e:
        print(f"Error opening YouTube: {e}")
        return "Error opening YouTube"

def process_command(command):
    try:
        if "open notepad" in command:
            try:
                subprocess.Popen("notepad")
                return "Opening Notepad."
            except:
                return "Could not open Notepad."
        
        elif "open calculator" in command:
            try:
                subprocess.Popen("calc")
                return "Opening Calculator."
            except:
                return "Could not open Calculator."
        
        elif "calculate" in command:
            speak("Say your calculation.")
            calculation = listen()
            try:
                # Clean up the calculation string
                calc_str = calculation.replace("x", "").replace("plus", "+").replace("minus", "-").replace("divided by", "/").replace("times", "")
                result = eval(calc_str)
                return f"The result is {result}"
            except Exception:
                return "Sorry, I couldn't calculate that."
        
        elif "open chrome" in command:
            try:
                if platform.system() == "Windows":
                    subprocess.Popen("start chrome", shell=True)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", "-a", "Google Chrome"])
                else:
                    subprocess.Popen(["google-chrome"])
                return "Opening Google Chrome."
            except:
                return "Could not open Chrome."
        
        elif "search google for" in command:
            query = command.replace("search google for", "").strip()
            if query:
                return google_search(query)
            else:
                return "Please specify what to search for."
        
        elif "search youtube for" in command:
            query = command.replace("search youtube for", "").strip()
            if query:
                return youtube_search(query)
            else:
                return "Please specify what to search for."
        
        elif "open file" in command:
            speak("Please say the file name.")
            file_name = listen()
            if file_name and file_name != "":
                return open_file(file_name)
            else:
                return "I couldn't hear the file name clearly."
        
        elif "search in file" in command:
            speak("Say the file name.")
            file_name = listen()
            if file_name and file_name != "":
                speak("Say the word to search for.")
                keyword = listen()
                if keyword and keyword != "":
                    return search_file(file_name, keyword)
                else:
                    return "I couldn't hear the search keyword clearly."
            else:
                return "I couldn't hear the file name clearly."
        
        elif "what is the time" in command or "time" in command:
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            return f"The time is {current_time}"
        
        elif "exit" in command or "stop" in command:
            return "Goodbye!"
        
        else:
            return "I didn't understand. Please repeat."
    
    except Exception as e:
        print(f"Error processing command: {e}")
        return "Sorry, there was an error processing your command."

def main():
    try:
        speak("Hello! I am your assistant.")
        speak("How may I help you?")
        speak("What would you like me to do?")
        
        while True:
            command = listen()
            if command and command != "":
                response = process_command(command)
                speak(response)
                print(f"Response: {response}")
                
                if response == "Goodbye!":
                    break
            else:
                print("No command heard, listening again...")
    
    except KeyboardInterrupt:
        speak("Goodbye!")
        print("Assistant stopped by user.")
    except Exception as e:
        print(f"Error in main function: {e}")
        speak("Sorry, there was an error. Goodbye!")

if _name_ == "_main_":
    main()