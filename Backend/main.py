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

PROJECT_HOME_PATH=os.getenv('PROJECT_HOME_PATH')

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
    global RECORDING
    if RECORDING:
        return jsonify({"status": "Already recording. Please stop the current recording first."})
    RECORDING = True
    threading.Thread(target=record_audio).start()
    return jsonify({"status": "Recording started"})

# API endpoint to stop recording and process audio
@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    global RECORDING, FRAMES, stream, p
    if not RECORDING:
        return jsonify({"status": "Error", "message": "No recording is in progress"})

    RECORDING = False

    # Save recorded audio to a temporary file
    temp_file = "temp_audio.wav"
    temp_file_path = os.path.join(PROJECT_HOME_PATH, 'Data', temp_file)
    wf = wave.open(temp_file_path, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(FRAMES))
    wf.close()

    # Get language preferences from the user
    input_language = request.json.get("inputLanguage", "en-US")  # Default to English
    output_language = request.json.get("outputLanguage", "en")  # Default to English

    # Ensure language codes are in correct format (e.g., 'hi-IN' -> 'hi')
    input_language = input_language.split('-')[0]  # e.g., 'hi-IN' -> 'hi'
    output_language = output_language.split('-')[0]  # e.g., 'hi' -> 'hi'

    # Speech-to-Text (STT)
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_file_path) as source:
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

    # Text-to-Speech (TTS)
    tts = gTTS(translated_text, lang=output_language)
    tts.save(translated_audio_file_path)

    # Clean up temporary files
    os.remove(temp_file_path)

    # Reset PyAudio and Stream to allow for next recording
    stream.close()
    p.terminate()

    # Send the new audio URL back in the response
    translated_audio_url = f"/static/{translated_audio_file_name}"
    return jsonify({
        "status": "Recording stopped",
        "audio_url": translated_audio_url,
        "original_text": input_text,
        "translated_text": translated_text
    })

if __name__ == "__main__":
    app.run(debug=True)
