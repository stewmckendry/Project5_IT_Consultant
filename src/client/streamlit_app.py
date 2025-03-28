# streamline_app.py – client-facing Streamlit app

import os
import sys
import streamlit as st
import requests

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.file_loader import load_report_text_from_file
from src.utils.text_processing import split_report_into_sections
from src.server.report_review_runner import run_full_report_review
from src.utils.export_utils import export_report_to_markdown_and_pdf


BACKEND_URL = "http://localhost:8001/review_report/"

def upload_and_review_report(file):
    """
    Sends the uploaded file to the FastAPI backend for processing.
    """
    if file is not None:
        files = {"file": (file.name, file, "text/plain")}
        response = requests.post(BACKEND_URL, files=files)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            st.error(f"⚠️ Server error: {response.status_code}")
    return None


st.title("📊 AI-Powered Consulting Report Review")

uploaded_file = st.file_uploader("Upload your consulting report (.txt)", type=["txt"])

if uploaded_file:
    with st.spinner("🔍 Analyzing report... please wait..."):
        result = upload_and_review_report(uploaded_file)

    # After successful result
    if result and result["status"] == "success":
        st.success("✅ Review complete!")
        st.markdown("### Final Summary")
        st.markdown(result["result"]["final_summary"])

        st.markdown("### Top Issues")
        st.markdown(result["result"].get("top_issues", "None found."))

        st.markdown("### Section Scores")
        section_scores = result["result"].get("section_scores", {})
        for section, scores in section_scores.items():
            st.markdown(f"#### {section}")
            st.markdown(scores)

        # Download file paths
        markdown_path = result["result"]["markdown_download"]
        pdf_path = result["result"]["pdf_download"]

        # Preview and download buttons
        with st.expander("🔍 Preview Markdown Report"):
            with open(markdown_path, "r") as f:
                st.code(f.read(), language="markdown")


        if os.path.exists(markdown_path):
            with open(markdown_path, "rb") as f:
                st.download_button("⬇️ Download Markdown", f, file_name="consultant_ai_report.md")

        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name="consultant_ai_report.pdf")
        

    elif result:
        st.error(f"❌ {result['message']}")
