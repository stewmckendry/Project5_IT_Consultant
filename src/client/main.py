from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from utils.react_agent import process_report_and_generate_summary
import shutil
import os

app = FastAPI()

# Allow CORS so frontend can call API locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploaded_reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class ReviewRequest(BaseModel):
    notes: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Consultant Report Review API"}

@app.post("/upload/")
def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "message": "File uploaded successfully."}

@app.post("/review/")
def review_file(filename: str = Form(...), notes: str = Form("")):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found."}

    markdown_path, pdf_path = process_report_and_generate_summary(file_path, user_notes=notes)
    return {
        "message": "Report processed successfully.",
        "markdown_path": markdown_path,
        "pdf_path": pdf_path
    }

@app.get("/download/pdf/{filename}")
def download_pdf(filename: str):
    file_path = os.path.join("output", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/pdf', filename=filename)
    return {"error": "File not found."}

@app.get("/download/md/{filename}")
def download_md(filename: str):
    file_path = os.path.join("output", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='text/markdown', filename=filename)
    return {"error": "File not found."}
