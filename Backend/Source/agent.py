# Required Imports
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import tool
import speech_recognition as sr
from gtts import gTTS
import os
import pygame

# Initialize Pygame for audio playback
pygame.mixer.init()

# Initialize the LLM with Google API key
llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro', google_api_key='')

def generate_response(query):
    return llm.invoke(query).content

# -----------------------------
# Text-to-Speech Function
# -----------------------------
def text_to_speech(text, language='en'):
    try:
        tts = gTTS(text=text, lang=language)
        tts.save('output.mp3')
        pygame.mixer.music.load('output.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Text-to-Speech Error: {str(e)}")

# -----------------------------
# Speech Recognition Function
# -----------------------------
def speech_to_text(language='en'):
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
        return recognizer.recognize_google(audio, language=language)
    except Exception as e:
        print(f"Speech Recognition Error: {str(e)}")
        return None

# -----------------------------
# Translation Tool
# -----------------------------
@tool
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text from source language to target language."""
    try:
        print(f"Translating '{text}' from {source_lang} to {target_lang}")
        llm_response = generate_response(f"Translate this text: '{text}' from {source_lang} to {target_lang}.")
        return llm_response
    except Exception as e:
        print(f"Translation Error: {str(e)}")
        return "Translation failed."

# -----------------------------
# Teacher Speech Tool
# -----------------------------
@tool
def teacher_speech(language: str):
    """Capture teacher's speech and process it for the student."""
    try:
        teacher_text = speech_to_text(language=language)
        print(f"Teacher said: {teacher_text}")
        return teacher_text
    except Exception as e:
        print(f"Teacher Speech Error: {str(e)}")
        return "Failed to capture teacher's speech."

# -----------------------------
# Student Speech Tool
# -----------------------------
@tool
def student_speech(language: str):
    """Capture student's speech and process it for the teacher."""
    try:
        student_text = speech_to_text(language=language)
        print(f"Student said: {student_text}")
        return student_text
    except Exception as e:
        print(f"Student Speech Error: {str(e)}")
        return "Failed to capture student's speech."

# -----------------------------
# Agent Setup
# -----------------------------
tools = [translate_text, teacher_speech, student_speech]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant facilitating multilingual teacher-student communication."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create LangChain Agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# -----------------------------
# Interaction Loop
# -----------------------------
def interaction_loop():
    try:
        # Ask Teacher for their language
        text_to_speech("Teacher, please say your language code. For example, 'en' for English or 'es' for Spanish.", 'en')
        teacher_lang = speech_to_text(language='en')
        print(f"Teacher language: {teacher_lang}")

        # Ask Student for their language
        text_to_speech("Student, please say your language code. For example, 'en' for English or 'es' for Spanish.", 'en')
        student_lang = speech_to_text(language='en')
        print(f"Student language: {student_lang}")

        while True:
            # Teacher speaks
            text_to_speech("Teacher, please speak.", teacher_lang)
            teacher_text = agent_executor.invoke({"input": f"Capture teacher speech in {teacher_lang}"})['output']

            # Translate Teacher's speech to Student's language
            translated_for_student = agent_executor.invoke({
                "input": f"Translate '{teacher_text}' from {teacher_lang} to {student_lang}"
            })['output']

            text_to_speech(translated_for_student, student_lang)

            # Student responds
            text_to_speech("Student, please respond.", student_lang)
            student_text = agent_executor.invoke({"input": f"Capture student speech in {student_lang}"})['output']

            # Translate Student's speech to Teacher's language
            translated_for_teacher = agent_executor.invoke({
                "input": f"Translate '{student_text}' from {student_lang} to {teacher_lang}"
            })['output']

            text_to_speech(translated_for_teacher, teacher_lang)

            # Ask if they want to continue
            text_to_speech("Do you want to continue? Say yes or no.", teacher_lang)
            confirmation = speech_to_text(language=teacher_lang)
            if confirmation.lower() != 'yes':
                text_to_speech("Goodbye!", teacher_lang)
                break

    except Exception as e:
        print(f"Interaction Loop Error: {str(e)}")
        text_to_speech("An error occurred, restarting the session.", 'en')

# -----------------------------
# Start Interaction
# -----------------------------
if __name__ == '__main__':
    interaction_loop()
