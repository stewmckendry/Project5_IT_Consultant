from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uuid
from src.server.proposal_eval import evaluate_proposal
from src.utils.logging_utils import log_phase

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

from fastapi import UploadFile, File, Form, APIRouter
from src.server.runner import run_multi_proposal_evaluation
from pathlib import Path
import tempfile
import shutil

@router.post("/evaluate")
async def evaluate_proposals(
    rfp_file: UploadFile = File(...),
    proposal_files: list[UploadFile] = File(...),
    model: str = Form("gpt-3.5-turbo")
):
    # 1. Save uploaded files to a temp directory
    temp_dir = Path(tempfile.mkdtemp())
    rfp_path = temp_dir / rfp_file.filename
    with rfp_path.open("wb") as f:
        f.write(await rfp_file.read())

    proposals = {}
    for f in proposal_files:
        content = await f.read()
        proposal_path = temp_dir / f.filename
        with proposal_path.open("wb") as out:
            out.write(content)
        proposals[f.filename] = proposal_path.read_text()

    # 2. Run evaluation
    results, summary_text, report_meta = run_multi_proposal_evaluation(
        proposals=proposals,
        rfp_file=str(rfp_path),
        model=model
    )

    # 3. Return summary (or download link)
    return {
        "status": "success",
        "summary": summary_text,
        "report_path": report_meta.get("summary_path", "")
    }


@app.get("/report", response_class=HTMLResponse)
async def view_report():
    return "<h2>🧾 Reports not yet implemented — coming soon!</h2>"
