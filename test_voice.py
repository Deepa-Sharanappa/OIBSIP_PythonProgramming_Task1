import speech_recognition as sr
import pyttsx3

# Initialize speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak something...")
    audio = recognizer.listen(source)

try:
    text = recognizer.recognize_google(audio)
    print("You said:", text)
    speak("You said " + text)
except Exception as e:
    print("Error:", e)
    speak("Sorry, I could not understand.")
    
