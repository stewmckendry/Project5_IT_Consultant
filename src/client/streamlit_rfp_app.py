import streamlit as st
import requests

API_URL = "http://localhost:8000"  # Update if deploying remotely

st.set_page_config(page_title="RFP Evaluator", layout="centered")
st.title("📄 AI-Powered RFP Evaluator")

# --- Upload Files ---
st.subheader("Step 1: Upload Files")
rfp_file = st.file_uploader("Upload RFP File", type=["txt", "md", "pdf", "docx"], key="rfp")
proposal_files = st.file_uploader("Upload Vendor Proposals", type=["txt", "md", "pdf", "docx"], accept_multiple_files=True)

# --- Submit Evaluation ---
if st.button("🚀 Run Evaluation"):
    if not rfp_file or not proposal_files:
        st.warning("Please upload both an RFP and at least one proposal.")
    else:
        with st.spinner("Evaluating proposals... this may take a minute ☕"):
            files = [("files", (rfp_file.name, rfp_file, rfp_file.type))]
            for p in proposal_files:
                files.append(("files", (p.name, p, p.type)))

            response = requests.post(f"{API_URL}/evaluate", files=files)

            if response.status_code == 200:
                st.success("Evaluation complete! ✅")
                result = response.json()
                # Save file paths and run_id for preview/download
                st.session_state["file_paths"] = result.get("file_paths", {})
                st.session_state["run_id"] = result.get("run_id")
                # Optional: show summary directly
                summary = result.get("final_summary_text")
                if summary:
                    st.subheader("📊 Final Summary")
                    st.markdown(summary)
                if "file_paths" in st.session_state and "run_id" in st.session_state:
                    run_id = st.session_state["run_id"]
                    file_paths = st.session_state["file_paths"]
                    st.markdown("---")
                    st.subheader("📂 Preview Reports")
                    tab1, tab2, tab3, tab4 = st.tabs(["📋 Final Summary", "🏢 Vendor Reports", "🛠️ Log Summary", "⬇️ Download Reports"])
                    # --- Final Summary Tab ---
                    with tab1:
                        st.markdown("### 📋 Final Summary Report")
                        html = requests.get(f"{API_BASE}/preview/{run_id}/final_summary_report").text
                        st.components.v1.html(html, height=800, scrolling=True)
                    # --- Vendor Reports Tab ---
                    with tab2:
                        st.markdown("### 🏢 Proposal Evaluations")
                        for vendor in sorted(file_paths["proposal_reports"]):
                            filename = f"{vendor}_evaluation".replace(" ", "%20")
                            st.markdown(f"#### {vendor}")
                            html = requests.get(f"{API_BASE}/preview/{run_id}/{filename}").text
                            st.components.v1.html(html, height=600, scrolling=True)
                    # --- Log Summary Tab ---
                    with tab3:
                        st.markdown("### 🛠️ Evaluation Log Summary")
                        html = requests.get(f"{API_BASE}/preview/{run_id}/logging_summary_report{run_id}").text
                        st.components.v1.html(html, height=800, scrolling=True)
                    # --- Download Reports Tab ---
                    with tab4:
                            st.markdown("### ⬇️ Download Reports")

                            # Download ZIP of all files
                            zip_url = f"{API_BASE}/download-all/{run_id}"
                            st.download_button("📦 Download All Reports (ZIP)", zip_url, file_name="all_reports.zip")

                            st.markdown("### 📄 Individual Downloads")

                            # --- Final Summary ---
                            st.markdown("#### 📋 Final Summary Report")
                            for ext in ["pdf", "html", "md"]:
                                download_url = f"{API_BASE}/download/{run_id}/final_summary_report.{ext}"
                                st.markdown(f"[Download {ext.upper()}]({download_url})")

                            # --- Vendor Reports ---
                            st.markdown("#### 🏢 Vendor Reports")
                            for vendor in sorted(file_paths["proposal_reports"]):
                                base_filename = f"{vendor}_evaluation"
                                for ext in ["pdf", "html", "md"]:
                                    download_url = f"{API_BASE}/download/{run_id}/{base_filename}.{ext}"
                                    st.markdown(f"- **{vendor}** – [{ext.upper()}]({download_url})")

                            # --- Logging Report ---
                            st.markdown("#### 🛠️ Logging Summary Report")
                            log_filename = f"logging_summary_report_{run_id}"
                            for ext in ["pdf", "html", "md"]:
                                download_url = f"{API_BASE}/download/{run_id}/{log_filename}.{ext}"
                                st.markdown(f"[Download {ext.upper()}]({download_url})")


            else:
                st.error("Evaluation failed. Please check the server logs.")
        
        