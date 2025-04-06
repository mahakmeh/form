import streamlit as st
from fpdf import FPDF
import tempfile

# Define the questions
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

# Session state initialization
if "current_step" not in st.session_state:
    st.session_state["current_step"] = 0
if "responses" not in st.session_state:
    st.session_state["responses"] = {}

# App title
st.title("Medical Questionnaire - Manual Input Version")

# Display each question
for idx, item in enumerate(questions):
    st.subheader(item["question"])
    if idx == st.session_state["current_step"]:
        response = st.text_input(
            "Answer:",
            key=f"input_{idx}",
            value=st.session_state["responses"].get(item["question"], "")
        )
        st.session_state["responses"][item["question"]] = response
    else:
        st.text_input(
            "Answer:",
            value=st.session_state["responses"].get(item["question"], ""),
            key=f"display_{idx}",
            disabled=True
        )

# Navigation controls
col1, col2 = st.columns(2)
with col1:
    if st.button("Previous") and st.session_state["current_step"] > 0:
        st.session_state["current_step"] -= 1
        st.rerun()
with col2:
    if st.button("Next") and st.session_state["current_step"] < len(questions) - 1:
        st.session_state["current_step"] += 1
        st.rerun()

# Progress bar
st.progress((st.session_state["current_step"] + 1) / len(questions))

# Export to PDF function
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

# Export button
if st.button("Export Report as PDF"):
    export_to_pdf()
