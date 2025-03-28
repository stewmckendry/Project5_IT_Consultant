# streamline_app.py – client-facing Streamlit app

import streamlit as st
from src.utils.file_loader import load_report_text_from_file
from src.utils.text_processing import split_report_into_sections
from src.server.report_review_runner import run_full_report_review
from src.utils.export_utils import export_report_to_markdown_and_pdf

# App title and description
st.set_page_config(page_title="AI Consulting Report Reviewer", layout="wide")
st.title("📊 AI-Powered Consulting Report Reviewer")
st.markdown("Upload a consulting report and let the AI analyze each section for clarity, alignment, completeness, and more.")

# File uploader
uploaded_file = st.file_uploader("Upload your consulting report (TXT, PDF, or DOCX)", type=["txt", "pdf", "docx"])

# Processing options
max_steps = st.slider("Number of ReAct steps per section", min_value=1, max_value=10, value=5)
run_button = st.button("🔍 Run AI Review")

# Run review
if run_button and uploaded_file:
    with st.spinner("Processing your report with AI..."):
        # Step 1: Load report text
        report_text = load_report_text_from_file(uploaded_file)

        # Step 2: Split into sections
        report_sections = split_report_into_sections(report_text)

        # Step 3: Run full ReAct loop
        agent = run_full_report_review(report_sections, max_steps=max_steps)

        # Step 4: Export report
        export_report_to_markdown_and_pdf(agent)

        st.success("✅ AI review complete! Report exported to Markdown and PDF.")
        st.markdown("---")
        st.markdown("📄 Download your outputs below:")

        # Show download links
        st.download_button(
            label="📥 Download Markdown Report",
            data=open("Outputs/consultant_ai_report.md", "rb").read(),
            file_name="consultant_ai_report.md",
            mime="text/markdown"
        )

        st.download_button(
            label="📥 Download PDF Report",
            data=open("Outputs/consultant_ai_report.pdf", "rb").read(),
            file_name="consultant_ai_report.pdf",
            mime="application/pdf"
        )

# Footer
st.markdown("---")
st.caption("Built with 🤖 by your AI Consultant.")
