import speech_recognition as sr
import pyttsx3
import datetime
import math
import webbrowser
import os
import wikipedia
import requests
import logging
logging.basicConfig(filename="assistant.log", level=logging.INFO)
import smtplib
from email.message import EmailMessage

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
        except:
            return ""

    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except:
        speak("Sorry, I did not understand.")
        return ""

def tell_time():
    time = datetime.datetime.now().strftime("%H:%M")
    speak("The current time is " + time)

def tell_date():
    today = datetime.datetime.now().strftime("%d %B %Y")
    speak("Today's date is " + today)

def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good Morning Deepa")
    elif hour < 18:
        speak("Good Afternoon Deepa")
    else:
        speak("Good Evening Deepa")

def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False
    
def get_current_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()

        city = data["city"]
        country = data["country"]

        return city, country

    except:
        speak("Unable to detect location.")
        return None, None

def get_weather(city=None):
    api_key = "YOUR_API_KEY"

    # If city not given → auto detect
    if city is None:
        city, country = get_current_location()
        if city is None:
            return
        speak(f"I detected your location as {city}, {country}.")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
    
        if data["cod"] != 200:
            speak("City not found.")
            return
    
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]

        speak(f"The temperature in {city} is {temp} degrees Celsius.")
        speak(f"Weather condition is {description}.")
        speak(f"Humidity is {humidity} percent.")

    except Exception as e:
        speak("Sorry, I am unable to fetch weather information right now.")
        print(e)

def get_5day_forecast(city):
    api_key = "YOUR_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)
    data = response.json()

    if data["cod"] != "200":
        speak("City not found.")
        return

    speak(f"Here is the 5 day forecast for {city}.")

    for i in range(0, 40, 8):  # every 24 hours
        date = data["list"][i]["dt_txt"].split(" ")[0]
        temp = data["list"][i]["main"]["temp"]
        description = data["list"][i]["weather"][0]["description"]

        speak(f"On {date}, temperature will be {temp} degree Celsius with {description}.")


def get_weather_alerts(lat, lon):
    api_key = "YOUR_API_KEY"
    
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    data = response.json()
    
    if "alerts" in data:
        for alert in data["alerts"]:
            event = alert["event"]
            description = alert["description"]
            
            speak(f"Weather alert: {event}")
            speak(description)
    else:
        speak("There are no weather alerts for your location.")

def get_coordinates():
    response = requests.get("http://ip-api.com/json/")
    data = response.json()
    return data["lat"], data["lon"]

def send_email(recipient_email, subject, body):
    try:
        sender_email = "your_email@gmail.com"
        app_password = "YOUR_APP_PASSWORD"

        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.set_content(body)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()

        speak("Email has been sent successfully.")

    except Exception as e:
        speak("Sorry, I was unable to send the email.")
        print(e)

def process_email():
    speak("Please tell me the recipient email address.")
    recipient = input("Enter recipient email: ")
    if "@" not in recipient or "." not in recipient:
        speak("Invalid email address.")
        return

    speak("What should be the subject?")
    subject = listen()

    speak("What is the message?")
    body = listen()

    speak("Do you want me to send this email?")
    confirmation = listen()

    if "yes" in confirmation:
        send_email(recipient, subject, body)
    else:
        speak("Email cancelled.")

def main():
    greet_user()
    speak("Hello Deepa, I am your voice assistant.How can I assist you today?")

    while True:
        command = listen()
        logging.info(f"User said: {command}")
        
        if "hello" in command:
            speak("Hello! How can I help you?")

        elif "time" in command:
            tell_time()

        elif "date" in command or "today" in command:
            tell_date()

        elif "how are you" in command:
            print("I am doing great! How can I help you?")

        elif "open google" in command:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")
       
        elif "open youtube" in command:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        
        elif "search" in command:
            speak("What should I search for?")
            query = listen()
            webbrowser.open("https://www.google.com/search?q=" + query)

        elif "joke" in command:
            speak("Why do programmers prefer dark mode? Because light attracts bugs!")
        
        elif "open" in command:
            site = command.replace("open", "")
            speak("Opening " + site)
            webbrowser.open("https://www." + site + ".com")
        

        elif "calculate" in command:
            speak("What should I calculate?")
            expression = listen()
            try:
                result = eval(expression, {"__builtins__": None}, {"sqrt": math.sqrt})
                speak("The result is " + str(result))
            except:
                speak("Sorry, I could not calculate that.")

        elif "take note" in command:
                speak("What should I write?")
                note = listen()
                with open("notes.txt", "a") as file:
                    file.write(note + "\n")
                speak("Note saved successfully.")

        elif "open notepad" in command:
            speak("Opening Notepad")
            os.system("notepad")

        elif "open calculator" in command:
            speak("Opening Calculator")
            os.system("calc")

        elif "wikipedia" in command:
            speak("What should I search on Wikipedia?")
            topic = listen()
            try:
                result = wikipedia.summary(topic, sentences=2)
                speak(result)
            except Exception as e:
                print("Error:", e)
                speak("Sorry, I did not understand.")

        elif "weather" in command and "forecast" not in command:
            if "here" in command or "current location" in command:
                get_weather()
            else:
                speak("Please tell me the city name.")
                city = listen()
                get_weather(city)

        elif "forecast" in command:
                speak("Please tell me the city name.")
                city = listen()
                get_5day_forecast(city)
            
        elif "weather alert" in command:
            lat, lon = get_coordinates()
            get_weather_alerts(lat, lon)

        elif "email" in command or "send mail" in command:
            process_email()

        elif "exit" in command or "stop" in command:
            speak("Thank you for using your AI assistant. Have a great day Deepa!")
            break
        else:
            print("Sorry, I did not understand that.")




if __name__ == "__main__":
    main()
