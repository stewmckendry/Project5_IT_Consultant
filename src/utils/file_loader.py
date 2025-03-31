# file_loader.py – File input handling

from pathlib import Path
import docx # for Word documents
import fitz # for PDFs
import os
from typing import Dict
import PyPDF2

def load_report_text_from_file(filepath):
    """
    Loads text from a supported file format (txt, md, docx, pdf).
    """
    ext = Path(filepath).suffix.lower()

    if ext in [".txt", ".md"]:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".docx":
        doc = docx.Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])
    elif ext == ".pdf":
        doc = fitz.open(filepath)
        return "\n".join([page.get_text() for page in doc])
    else:
        raise ValueError("Unsupported file format. Use .txt, .md, .docx, or .pdf")



def load_proposals_from_folder(folder_path: str) -> Dict[str, str]:
    """
    Loads all proposal files in a folder (supports .txt, .pdf, .docx) and returns a dict.
    Keys are inferred from filenames (e.g., 'Vendor A.txt' → 'Vendor A').
    """
    proposals = {}
    folder = Path(folder_path)

    for file in folder.glob("*"):
        vendor_name = file.stem  # e.g., "Vendor A"

        if file.suffix == ".txt":
            proposals[vendor_name] = file.read_text(encoding="utf-8")

        elif file.suffix == ".docx":
            doc = docx.Document(file)
            proposals[vendor_name] = "\n".join([para.text for para in doc.paragraphs])

        elif file.suffix == ".pdf":
            with open(file, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
                proposals[vendor_name] = text

    return proposals


def load_rfp_criteria(filepath: str) -> list:
    """
    Loads RFP evaluation criteria from a file.
    Each line should represent one criterion.
    """
    text = load_report_text_from_file(filepath)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Remove numbering if present
    criteria = [line.split('.', 1)[-1].strip() if '.' in line else line for line in lines]
    return criteria

