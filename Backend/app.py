from flask import Flask, jsonify, request
from flask_cors import CORS
from gtts import gTTS
import os
import wave
import uuid
import threading
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from googletrans import Translator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Vercel-specific: Use /tmp for temporary storage
PROJECT_HOME_PATH = "/tmp"
os.makedirs(os.path.join(PROJECT_HOME_PATH, "static"), exist_ok=True)

app = Flask(__name__, static_folder=os.path.join(PROJECT_HOME_PATH, "static"))
CORS(app)

# Audio settings
CHUNK = 1024
FORMAT = "int16"  # Format used by sounddevice
CHANNELS = 1
RATE = 44100
RECORDING = False
FRAMES = []
stream_thread = None

# Thread function for audio recording
def record_audio():
    global FRAMES, RECORDING
    FRAMES = []
    with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype=FORMAT, callback=callback):
        while RECORDING:
            sd.sleep(100)

# Callback function to capture audio data
def callback(indata, frames, time, status):
    global FRAMES
    FRAMES.append(indata.copy())

@app.route("/")
def home():
    return "Flask App Working"

@app.route("/start_recording", methods=["POST"])
def start_recording():
    global RECORDING, stream_thread
    if RECORDING:
        return jsonify({"status": "Already recording. Please stop the current recording first."})
    RECORDING = True
    stream_thread = threading.Thread(target=record_audio)
    stream_thread.start()
    return jsonify({"status": "Recording started"})

@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    global RECORDING, FRAMES
    if not RECORDING:
        return jsonify({"status": "Error", "message": "No recording is in progress"})

    RECORDING = False
    stream_thread.join()

    # Save recorded audio
    recorded_audio_file_name = f"{uuid.uuid4().hex}.wav"
    recorded_audio_file_path = os.path.join(PROJECT_HOME_PATH, "static", recorded_audio_file_name)

    # Convert numpy array to wave
    wf = wave.open(recorded_audio_file_path, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)  # 2 bytes for 'int16' format
    wf.setframerate(RATE)
    wf.writeframes(b"".join([frame.tobytes() for frame in FRAMES]))
    wf.close()

    # Process audio: Speech-to-Text (STT)
    recognizer = sr.Recognizer()
    with sr.AudioFile(recorded_audio_file_path) as source:
        audio = recognizer.record(source)

    input_language = request.json.get("inputLanguage", "en-US")
    output_language = request.json.get("outputLanguage", "en")

    try:
        input_text = recognizer.recognize_google(audio, language=input_language)
    except sr.UnknownValueError:
        return jsonify({"status": "Error", "message": "Could not understand audio"})
    except sr.RequestError as e:
        return jsonify({"status": "Error", "message": f"Speech recognition service unavailable: {e}"})

    # Translate text
    translator = Translator()
    try:
        translated_text = translator.translate(input_text, src=input_language.split("-")[0], dest=output_language).text
    except Exception as e:
        return jsonify({"status": "Error", "message": f"Translation failed: {str(e)}"})

    # Generate TTS audio
    translated_audio_file_name = f"{uuid.uuid4().hex}.mp3"
    translated_audio_file_path = os.path.join(PROJECT_HOME_PATH, "static", translated_audio_file_name)
    tts = gTTS(translated_text, lang=output_language)
    tts.save(translated_audio_file_path)

    return jsonify({
        "status": "Recording stopped",
        "input_audio_url": f"/static/{recorded_audio_file_name}",
        "translated_audio_url": f"/static/{translated_audio_file_name}",
        "original_text": input_text,
        "translated_text": translated_text
    })

# Remove Flask's app.run() for Vercel compatibility
