import speech_recognition as sr
import webbrowser
import pyttsx3
import requests # type: ignore
import os

# Optional imports
try:
    import musicLibrary  # Make sure this file exists and has a 'music' dictionary
except ImportError:
    musicLibrary = None

try:
    from gtts import gTTS # type: ignore
    import pygame # type: ignore
    use_gtts = True
except ImportError:
    use_gtts = False  # Fallback to pyttsx3 if gTTS or pygame isn't available

recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = "37f097e098c24d3395a1a38a7a8e8e00"

# ---------- SPEAK FUNCTION ----------
def speak(text):
    if use_gtts:
        try:
            tts = gTTS(text)
            tts.save('temp.mp3') 

            pygame.mixer.init()
            pygame.mixer.music.load('temp.mp3')
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            os.remove("temp.mp3")
        except Exception as e:
            print(f"gTTS failed, falling back to pyttsx3: {e}")
            engine.say(text)
            engine.runAndWait()
    else:
        engine.say(text)
        engine.runAndWait()

# ---------- PROCESS COMMAND ----------
def processCommand(c):
    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")

    elif c.startswith("play") and musicLibrary:
        try:
            song = c.split(" ", 1)[1]
            link = musicLibrary.music.get(song)
            if link:
                speak(f"Playing {song}")
                webbrowser.open(link)
            else:
                speak(f"Sorry, I don't have {song} in my library.")
        except IndexError:
            speak("Please specify the song name after 'play'.")

    elif "news" in c:
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
            if r.status_code == 200:
                articles = r.json().get('articles', [])
                for article in articles[:5]:  # Limit to 5 headlines
                    speak(article['title'])
            else:
                speak("Failed to fetch news.")
        except Exception as e:
            speak("An error occurred while fetching news.")
            print("News error:", e)

    else:
        speak("I did not understand that command.")

# ---------- MAIN ----------
if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=2)
                word = recognizer.recognize_google(audio)

            if word.lower() == "jarvis":
                speak("Yes?")
                with sr.Microphone() as source:
                    print("Listening for command...")
                    audio = recognizer.listen(source, timeout=8, phrase_time_limit=6)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)

        except sr.WaitTimeoutError:
            print("Timeout: No speech detected.")
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except Exception as e:
            print("Error:", e)
