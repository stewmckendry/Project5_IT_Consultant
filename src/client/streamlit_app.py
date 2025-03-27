import streamlit as st
from pathlib import Path
from docx import Document
import fitz  # PyMuPDF for PDFs

from utils.report_utils import split_report_into_sections
from utils.agent import ReActConsultantAgent
from utils.openai_utils import call_openai_with_tracking
from utils.report_utils import run_react_loop_check_withTool, export_report_to_markdown

st.set_page_config(page_title="Consultant AI", layout="wide")
st.title("🧠 AI-Powered Report Reviewer")
st.markdown("Upload a consulting report and get expert-level review, insights, scoring, and recommendations.")

uploaded_file = st.file_uploader("Upload a report (PDF, Word, or Markdown)", type=["pdf", "docx", "md"])

def extract_text_from_file(file):
    if file.name.endswith(".pdf"):
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in pdf])
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.name.endswith(".md"):
        return file.read().decode("utf-8")
    return ""

if uploaded_file:
    raw_text = extract_text_from_file(uploaded_file)
    st.subheader("📄 Report Preview")
    st.text_area("Raw Report Content", raw_text[:2000] + "...", height=200)

    if st.button("🤖 Run AI Review"):
        with st.spinner("Thinking..."):
            report_sections = split_report_into_sections(raw_text)
            agent = ReActConsultantAgent(section_name="Full Report", section_text="")

            for name, text in report_sections.items():
                agent.section_name = name
                agent.section_text = text
                run_react_loop_check_withTool(agent, max_steps=5)

            final_summary = agent.memory.get("final_summary", "No summary generated.")
            st.subheader("✅ Final Summary")
            st.markdown(final_summary)

            md_file = "consultant_ai_report.md"
            export_report_to_markdown(agent, filename=md_file)
            st.success("📄 Report exported to Markdown.")

            with open(md_file, "r") as f:
                st.download_button("⬇️ Download Markdown", f.read(), file_name="Consultant_Report.md")
