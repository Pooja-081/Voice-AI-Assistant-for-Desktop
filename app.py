
from flask import Flask, render_template, request, jsonify
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

def search_file(file_path, keyword):
    """Search for keyword in file with better encoding handling"""
    try:
        # Try different encodings
        encodings = ['utf-8', 'utf-16', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as file:
                    content = file.read()
                    if keyword.lower() in content.lower():
                        return True
                break
            except UnicodeDecodeError:
                continue
        
        return False
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error searching file: {e}")
        return False

def open_file(file_path):
    """Open file with cross-platform compatibility"""
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
        return True
    except Exception as e:
        print(f"Error opening file: {e}")
        return False

def google_search(query):
    try:
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
        # Try different selectors for search results
        selectors = [".BNeawe.s3v9rd.AP7Wnd", ".VwiC3b", ".hgKElc", ".g .s"]
        for selector in selectors:
            results = [snippet.get_text() for snippet in soup.select(selector)][:2]
            if results:
                break
        
        if results:
            speak("Here are the top results.")
            for result in results:
                speak(result[:200])  # Limit to first 200 characters
        else:
            speak("No results found, but I've opened the search in your browser.")
        
        webbrowser.open(url)
        return results
    except Exception as e:
        print(f"Error in Google search: {e}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak("I've opened the search in your browser.")
        return []

def search_youtube(query):
    try:
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"Searching YouTube for {query}"
    except Exception as e:
        print(f"Error opening YouTube: {e}")
        return "Error opening YouTube"

def process_command(command):
    response = "I didn't understand. Please repeat."
    
    try:
        if "open file" in command:
            speak("Please say the file name.")
            file_name = listen()
            
            if file_name and file_name != "":
                file_path = find_file(file_name)
                if file_path:
                    if open_file(file_path):
                        response = f"Opening {os.path.basename(file_path)}"
                        speak(response)
                    else:
                        response = "Could not open the file."
                        speak(response)
                else:
                    response = f"File '{file_name}' not found in common directories."
                    speak(response)
            else:
                response = "I couldn't hear the file name clearly."
                speak(response)
        
        elif "search in file" in command:
            speak("Say the file name.")
            file_name = listen()
            
            if file_name and file_name != "":
                speak("Say the word to search for.")
                keyword = listen()
                
                if keyword and keyword != "":
                    file_path = find_file(file_name)
                    if file_path:
                        if search_file(file_path, keyword):
                            response = f"Yes, '{keyword}' was found in {os.path.basename(file_path)}."
                        else:
                            response = f"No, '{keyword}' was not found in {os.path.basename(file_path)}."
                        speak(response)
                    else:
                        response = f"File '{file_name}' not found."
                        speak(response)
                else:
                    response = "I couldn't hear the search keyword clearly."
                    speak(response)
            else:
                response = "I couldn't hear the file name clearly."
                speak(response)
        
        elif "open notepad" in command:
            try:
                subprocess.Popen("notepad")
                response = "Opening Notepad."
                speak(response)
            except:
                response = "Could not open Notepad."
                speak(response)
        
        elif "open calculator" in command:
            try:
                subprocess.Popen("calc")
                response = "Opening Calculator."
                speak(response)
            except:
                response = "Could not open Calculator."
                speak(response)
        
        elif "calculate" in command:
            speak("Say your calculation.")
            calculation = listen()
            try:
                # Clean up the calculation string
                calc_str = calculation.replace("x", "").replace("plus", "+").replace("minus", "-").replace("divided by", "/").replace("times", "")
                result = eval(calc_str)
                response = f"The result is {result}"
            except:
                response = "Sorry, I couldn't calculate that."
            speak(response)
        
        elif "open chrome" in command:
            try:
                subprocess.Popen("start chrome", shell=True)
                response = "Opening Google Chrome."
                speak(response)
            except:
                response = "Could not open Chrome."
                speak(response)
        
        elif "search google for" in command:
            query = command.replace("search google for", "").strip()
            if query:
                results = google_search(query)
                response = f"Searching Google for {query}"
            else:
                response = "Please specify what to search for."
                speak(response)
        
        elif "search youtube for" in command:
            query = command.replace("search youtube for", "").strip()
            if query:
                response = search_youtube(query)
                speak(response)
            else:
                response = "Please specify what to search for."
                speak(response)
        
        elif "what is the time" in command or "time" in command:
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            response = f"The time is {current_time}"
            speak(response)
        
        elif "exit" in command or "stop" in command:
            speak("Goodbye!")
            return False, "Goodbye!"
    
    except Exception as e:
        print(f"Error processing command: {e}")
        response = "Sorry, there was an error processing your command."
        speak(response)
    
    return True, response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        command = data.get("command", "").lower()
        if command:
            continue_loop, response = process_command(command)
            return jsonify({"response": response, "continue": continue_loop})
        else:
            return jsonify({"response": "No command received"})
    except Exception as e:
        print(f"Error in process route: {e}")
        return jsonify({"response": "Error processing request"})

if __name__ == '__main__':
    try:
        speak("Hello Pooja! I am your assistant. How may I help you?")
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error starting Flask app: {e}")