from fastapi import FastAPI, Request, UploadFile, File, Form, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
import uuid
from src.server.multi_agent_rfpevalrunner import run_multi_proposal_evaluation
from src.utils.logging_utils import log_phase
from pathlib import Path
import tempfile
import shutil
from typing import List
import os
from src.utils.file_loader import process_uploaded_files  # if you save it as a separate helper
from zipfile import ZipFile

app = FastAPI(title="RFP Evaluation API", version="1.0")

# -------------------------------
# Data Models
# -------------------------------

class EvaluationRequest(BaseModel):
    vendor_name: str
    proposal_text: str
    rfp_criteria: list  # list of dicts: [{"name": "Criterion 1"}, ...]

# -------------------------------
# Routes
# -------------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h1>📝 RFP Evaluation System</h1>
    <p>Use the <code>/evaluate</code> route to submit vendor proposals for evaluation.</p>
    """

@app.post("/evaluate")
async def evaluate(files: List[UploadFile] = File(...)):
    try:
        proposals, rfp_path = process_uploaded_files(files)
        result = run_multi_proposal_evaluation(proposals=proposals, rfp_file=rfp_path)
        return JSONResponse(content=result["file_paths"])
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

BASE_OUTPUT_DIR = Path("outputs/proposal_eval_reports")
VALID_EXTENSIONS = {"pdf", "html", "md"}
    
@app.get("/preview/{run_id}/{filename}")
async def preview_report(run_id: str, filename: str):
    file_path = BASE_OUTPUT_DIR / run_id / f"{filename}.html"
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    content = file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=content)

@app.get("/download/{run_id}/{filename}.{ext}")
async def download_report(run_id: str, filename: str, ext: str):
    if ext not in VALID_EXTENSIONS:
        return JSONResponse(status_code=400, content={"error": f"Unsupported extension: {ext}"})
    file_path = BASE_OUTPUT_DIR / run_id / f"{filename}.{ext}"
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(file_path, media_type="application/octet-stream", filename=f"{filename}.{ext}")

@app.get("/reports/list/{run_id}")
async def list_all_reports(run_id: str):
    """
    Returns a list of available reports (proposal reports, summary, logs).
    """
    files = list(BASE_OUTPUT_DIR.glob(f"{run_id}/*.*"))
    grouped = {}

    for f in files:
        base = f.stem.replace("_evaluation", "").replace("_report", "")
        ext = f.suffix.lstrip(".")
        if base not in grouped:
            grouped[base] = []
        grouped[base].append({"filename": f.name, "ext": ext, "path": str(f)})

    return grouped

@app.get("/download-all/{run_id}")
async def download_all_reports(run_id: str):
    zip_name = "all_reports.zip"
    zip_path = BASE_OUTPUT_DIR / run_id / zip_name
    run_dir = BASE_OUTPUT_DIR / run_id
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in run_dir.glob("*.*"):
            zipf.write(f, arcname=f.name)

    return FileResponse(zip_path, media_type="application/zip", filename=zip_name)

