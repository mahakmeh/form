import streamlit as st
import requests
from fpdf import FPDF
import tempfile
import os

# Gemini API key from Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

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

# Initialize session state
if "current_step" not in st.session_state:
    st.session_state["current_step"] = 0
if "responses" not in st.session_state:
    st.session_state["responses"] = {}

# Title
st.title("🩺 Medical Questionnaire (Voice Friendly)")

# Step-wise form
current = st.session_state["current_step"]
question_obj = questions[current]
question = question_obj["question"]
q_type = question_obj["type"]

st.subheader(f"Q{current + 1}: {question}")

# Input field (simulate post-recorded transcription)
user_input = st.text_input("Paste your voice transcription or type answer manually")

# Process input using Gemini
if st.button("Submit Answer"):
    if user_input:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": f"You are filling out a medical form. Extract the relevant answer for the question '{question}' which requires a {q_type} response, from this text: {user_input}"
                            }
                        ]
                    }
                ]
            },
        )
        try:
            response_json = response.json()
            extracted = response_json["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            extracted = f"Error extracting answer: {e}"
        st.session_state["responses"][question] = extracted.strip()

        if current < len(questions) - 1:
            st.session_state["current_step"] += 1
            st.rerun()
    else:
        st.warning("Please paste the transcription or type something.")

# Show form progress
st.progress((current + 1) / len(questions))

# Display past responses
with st.expander("View All Responses"):
    for idx, item in enumerate(questions):
        ans = st.session_state["responses"].get(item["question"], "")
        st.markdown(f"**{item['question']}**: {ans}")

# PDF Export Function
def export_to_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Medical Questionnaire Report", ln=True, align='C')
    pdf.ln(10)

    for q, a in st.session_state["responses"].items():
        pdf.multi_cell(0, 10, f"{q}: {a}")
        pdf.ln()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        tmp_file.close()
        with open(tmp_file.name, "rb") as file:
            st.download_button("Download PDF", file, file_name="medical_report.pdf", mime="application/pdf")
        os.remove(tmp_file.name)

# Export Button
if st.button("Export Report as PDF"):
    export_to_pdf()
