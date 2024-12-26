from flask import Flask, render_template, jsonify, request
from flask_cors import CORS  
import pyaudio
import wave
import threading
from gtts import gTTS
import os
import speech_recognition as sr
from googletrans import Translator
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PROJECT_HOME_PATH=os.getenv('PROJECT_HOME_PATH')

# # os.makedirs(os.path.join(PROJECT_HOME_PATH, 'Data'),exist_ok=True)
# os.makedirs(os.path.join(PROJECT_HOME_PATH, 'static'),exist_ok=True)

PROJECT_HOME_PATH = "/tmp/project_home_path"  # Use a fixed path like `/tmp` for Vercel or another known directory

# Ensure necessary directories exist
os.makedirs(os.path.join(PROJECT_HOME_PATH, 'static'), exist_ok=True)

app = Flask(__name__, static_folder=os.path.join(PROJECT_HOME_PATH, 'static'))

CORS(app)

# Audio recording settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
FRAMES = []
RECORDING = False
stream = None
p = None

# Thread function for recording audio
def record_audio():
    print("inside record audio function !!!")
    global FRAMES, RECORDING, stream, p
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    FRAMES = []
    while RECORDING:
        data = stream.read(CHUNK)
        FRAMES.append(data)
    stream.stop_stream()
    stream.close()

# API endpoint to start recording
@app.route("/start_recording", methods=["POST"])
def start_recording():
    print("inside start recording function !!")
    data = request.get_json()
    print("Request JSON data:", data)

    input_language = data.get('inputLanguage', '')
    output_language = data.get('outputLanguage', '')

    print(f"Input Language: {input_language}, Output Language: {output_language}")
    
    global RECORDING
    if RECORDING:
        return jsonify({"status": "Already recording. Please stop the current recording first."})

    RECORDING = True
    print("Recording start :")
    threading.Thread(target=record_audio).start()
    print("Recording end !")

    return jsonify({"status": "Recording started", "inputLanguage": input_language, "outputLanguage": output_language})


# API endpoint to stop recording and process audio
@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    print("inside stop recording function !!")
    print("Request JSON data:", request.get_json())
    global RECORDING, FRAMES, stream, p
    if not RECORDING:
        return jsonify({"status": "Error", "message": "No recording is in progress"})

    RECORDING = False

    # Save recorded audio to a temporary file
    recorded_audio_file_name =f"{uuid.uuid4().hex}.wav"
    recorded_audio_file_path = os.path.join(PROJECT_HOME_PATH, 'static', recorded_audio_file_name)
    wf = wave.open(recorded_audio_file_path, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(FRAMES))
    wf.close()

    # Get language preferences from the user
    input_language = request.json.get("inputLanguage", "en-US")  # Default to English
    output_language = request.json.get("outputLanguage", "en")  # Default to English

    print("input_langugae receive :",input_language)
    print("output language receive :",output_language)


    # Ensure language codes are in correct format (e.g., 'hi-IN' -> 'hi')
    # input_language = input_language.split('-')[0]  # e.g., 'hi-IN' -> 'hi'
    # output_language = output_language.split('-')[0]  # e.g., 'hi' -> 'hi'

    # Speech-to-Text (STT)
    recognizer = sr.Recognizer()
    with sr.AudioFile(recorded_audio_file_path) as source:
        audio = recognizer.record(source)

    try:
        # Recognizing speech with the specified input language
        input_text = recognizer.recognize_google(audio, language=input_language)
    except sr.UnknownValueError:
        return jsonify({"status": "Error", "message": "Could not understand audio"})
    except sr.RequestError as e:
        return jsonify({"status": "Error", "message": f"Speech recognition service unavailable: {e}"})

    if not input_text:
        return jsonify({"status": "Error", "message": "No speech detected"})
    
    print("Input text is :",input_text)

    # Translation
    translator = Translator()
    try:
        if input_language == 'en' and output_language != "en":
            translated_text = translator.translate(input_text, src='en', dest=output_language).text
        elif output_language == 'en' and input_language != "en":
            translated_text = translator.translate(input_text, src=input_language, dest='en').text
        else:
            translated_text = translator.translate(input_text, src=input_language, dest=output_language).text
    except Exception as e:
        return jsonify({"status": "Error", "message": f"Translation failed: {str(e)}"})

    # Generate unique filename for the translated audio
    translated_audio_folder_path = os.path.join(PROJECT_HOME_PATH, 'static')
    translated_audio_file_name = f"{uuid.uuid4().hex}.mp3"
    translated_audio_file_path = os.path.join(translated_audio_folder_path, translated_audio_file_name)

    print("Translated text is :",translated_text)
    # Text-to-Speech (TTS)
    tts = gTTS(translated_text, lang=output_language)
    tts.save(translated_audio_file_path)

    # Clean up temporary files
    # os.remove(temp_file_path)

    # Reset PyAudio and Stream to allow for next recording
    stream.close()
    p.terminate()

    # Send the new audio URL back in the response
    translated_audio_url = f"http://localhost:5000/static/{translated_audio_file_name}"
    recorded_file_url=f"http://localhost:5000/static/{recorded_audio_file_name}"



    print(translated_audio_url)
    print(recorded_file_url)

    return jsonify({
        "status": "Recording stopped",
        "input_audio_url":recorded_file_url,
        "translated_audio_url": translated_audio_url,
        "original_text": input_text,
        "translated_text": translated_text
    })

if __name__ == "__main__":
    app.run(debug=True)
