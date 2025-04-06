import streamlit as st
import json
import requests
from fpdf import FPDF
import numpy as np
import wave
from google.cloud import speech
from google.oauth2 import service_account
import sounddevice as sd

# Initialize session state
if "current_step" not in st.session_state:
    st.session_state["current_step"] = 0
if "responses" not in st.session_state:
    st.session_state["responses"] = {}
if "recording_active" not in st.session_state:
    st.session_state["recording_active"] = False

# Define questionnaire
questions = [
    {"question": "Name", "type": "text"},
    {"question": "Age", "type": "number"},
    {"question": "Address", "type": "text"},
    {"question": "Contact number", "type": "number"},
    {"question": "Occupation", "type": "text"},
    {"question": "Socioeconomic status", "type": "text"},
    {"question": "Nearest health center", "type": "text"},
    {"question": "Time taken to reach health center", "type": "number"},
    {"question": "Means of transport to health center", "type": "text"},
]

# Audio functions
def record_audio():
    samplerate = 16000
    duration = 10
    st.sidebar.write("Recording... Click 'Stop Recording' when done.")
    st.session_state["recording"] = sd.rec(int(samplerate * duration), 
                                         samplerate=samplerate, 
                                         channels=1, 
                                         dtype=np.int16)
    st.session_state["recording_active"] = True

def stop_recording():
    if st.session_state.get("recording_active"):
        sd.stop()
        audio_data = st.session_state["recording"].tobytes()
        st.session_state["recording_active"] = False
        
        # Process audio directly without saving file
        transcript = transcribe_audio(audio_data)
        extracted_info = process_with_gemini(transcript, questions[st.session_state["current_step"]])
        
        current_question = questions[st.session_state["current_step"]]["question"]
        st.session_state["responses"][current_question] = extracted_info
        
        if st.session_state["current_step"] < len(questions) - 1:
            st.session_state["current_step"] += 1
            st.rerun()

# Google Cloud Speech-to-Text
def transcribe_audio(audio_data):
    try:
        creds = service_account.Credentials.from_service_account_info(
            json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        )
        client = speech.SpeechClient(credentials=creds)
        
        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        )
        
        response = client.recognize(config=config, audio=audio)
        return response.results[0].alternatives[0].transcript if response.results else ""
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return ""

# Gemini API
def process_with_gemini(text, question):
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={st.secrets['GEMINI_API_KEY']}"
        headers = {"Content-Type": "application/json"}
        
        prompt = f"Extract just the {question['type']} value for '{question['question']}' from: {text}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()

        if response_json.get("candidates"):
            return response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        st.error("No valid response from Gemini")
        return ""
    except Exception as e:
        st.error(f"Gemini API error: {str(e)}")
        return ""

# PDF Generation
def generate_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Medical Questionnaire Report", ln=True, align='C')
    pdf.ln(10)
    
    for q, a in st.session_state["responses"].items():
        pdf.multi_cell(0, 10, f"{q}: {a}")
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1')

# Streamlit UI
st.title("Medical Questionnaire - Voice Input System")

# Voice Input
st.sidebar.header("Voice Input")
if st.sidebar.button("Start Recording"):
    record_audio()
if st.sidebar.button("Stop Recording"):
    stop_recording()

# Questionnaire
for idx, item in enumerate(questions):
    st.subheader(item["question"])
    if idx == st.session_state["current_step"]:
        st.session_state["responses"][item["question"]] = st.text_input(
            "Answer:",
            key=f"input_{idx}",
            value=st.session_state["responses"].get(item["question"], ""),
        )
    else:
        st.text_input(
            "Answer:",
            value=st.session_state["responses"].get(item["question"], ""),
            key=f"display_{idx}",
            disabled=True
        )

st.progress((st.session_state["current_step"] + 1) / len(questions))

# Export
if st.button("Export Report as PDF"):
    pdf_bytes = generate_pdf()
    st.download_button(
        "Download PDF",
        pdf_bytes,
        file_name="medical_report.pdf",
        mime="application/pdf"
    )