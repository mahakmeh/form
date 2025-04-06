import streamlit as st
from fpdf import FPDF
import tempfile

# Questions to display
questions = [
    "Name",
    "Age",
    "Address",
    "Contact number",
    "Occupation",
    "Socioeconomic status",
    "Nearest health center",
    "Time taken to reach health center",
    "Means of transport to health center",
]

# Session state initialization
if "responses" not in st.session_state:
    st.session_state["responses"] = {q: "" for q in questions}
if "current_step" not in st.session_state:
    st.session_state["current_step"] = 0

st.title("Medical Questionnaire")

# Show current question
current_q = questions[st.session_state["current_step"]]
st.subheader(current_q)
response = st.text_input("Your answer:", value=st.session_state["responses"][current_q])
st.session_state["responses"][current_q] = response

# Navigation
col1, col2 = st.columns(2)
with col1:
    if st.button("Previous") and st.session_state["current_step"] > 0:
        st.session_state["current_step"] -= 1
        st.rerun()
with col2:
    if st.button("Next") and st.session_state["current_step"] < len(questions) - 1:
        st.session_state["current_step"] += 1
        st.rerun()

# Progress
st.progress((st.session_state["current_step"] + 1) / len(questions))

# Export to PDF
def export_to_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Medical Questionnaire Report", ln=True, align='C')
    pdf.ln(10)

    for q in questions:
        a = st.session_state["responses"][q]
        pdf.multi_cell(0, 10, f"{q}: {a}")
        pdf.ln()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        tmp_file.close()
        with open(tmp_file.name, "rb") as file:
            st.download_button("Download PDF", file, file_name="medical_report.pdf", mime="application/pdf")

if st.button("Export Report as PDF"):
    export_to_pdf()
