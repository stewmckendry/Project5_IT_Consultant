# file_loader.py – File input handling

from pathlib import Path
import docx # for Word documents
import fitz # for PDFs

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

