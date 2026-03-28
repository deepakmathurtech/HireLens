import speech_recognition as sr
import pyttsx3
import time

recognizer = sr.Recognizer()
is_speaking = False


def get_best_mic():

    mics = sr.Microphone.list_microphone_names()

    for index, name in enumerate(mics):

        if "hands-free" in name.lower() or "headset" in name.lower():
            print("Using microphone:", name)
            return index

    print("Using default microphone")

    return None


MIC_INDEX = get_best_mic()

microphone = sr.Microphone(device_index=MIC_INDEX)


def speak(text):

    global is_speaking

    is_speaking = True

    print("AI:", text)

    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    engine.setProperty('rate', 180)

    engine.say(text)
    engine.runAndWait()

    is_speaking = False


def listen():

    global is_speaking

    while is_speaking:
        time.sleep(0.1)

    with microphone as source:

        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        print("Listening...")

        audio = recognizer.listen(source, phrase_time_limit=20)

    try:

        text = recognizer.recognize_google(audio)

        print("User:", text)

        return text.lower()

    except:
        return ""
