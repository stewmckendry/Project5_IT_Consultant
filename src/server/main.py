# src/server/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from src.utils.file_loader import load_report_text_from_file
from src.server.report_review_runner import run_full_report_review
from src.utils.export_utils import export_report_to_markdown_and_pdf
from src.utils.text_processing import split_report_into_sections
from pathlib import Path
import shutil
import uuid

app = FastAPI()

@app.post("/review_report/")
async def review_report(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        temp_id = uuid.uuid4().hex
        base_dir = Path("Outputs") / temp_id
        base_dir.mkdir(parents=True, exist_ok=True)
        print(f"[DEBUG] Created base directory: {base_dir}")

        file_path = base_dir / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        print(f"[DEBUG] Saved uploaded file to: {file_path}")

        # Load and parse the report
        report_text = load_report_text_from_file(str(file_path))
        print(f"[DEBUG] Loaded report text from file: {file_path}")

        # ✅ Split into section dictionary
        report_sections = split_report_into_sections(report_text)
        print(f"[DEBUG] Split report into sections.")
    
        # Run full report review
        agent = run_full_report_review(report_sections)
        print(f"[DEBUG] Completed report review with agent.")

        # Export to markdown and PDF
        md_path, pdf_path = await export_report_to_markdown_and_pdf(agent, base_dir)
        print(f"[DEBUG] Exported report to Markdown: {md_path}, PDF: {pdf_path}")

        return {
            "status": "success",
            "result": {
            "final_summary": agent.memory.get("final_summary", ""),
            "top_issues": agent.memory.get("top_issues", ""),
            "section_scores": agent.memory.get("section_scores", {}),
            "markdown_download": str(md_path),
            "pdf_download": str(pdf_path)
            }
        }

    except Exception as e:
        print(f"[ERROR] Failed to process report: {str(e)}")
        return JSONResponse(
            content={"status": "error", "message": f"Failed to process report: {str(e)}"},
            status_code=500
        )

# For local testing
if __name__ == "__main__":
    uvicorn.run("src.server.main:app", host="127.0.0.1", port=8001, reload=True)
