# file_loader.py – File input handling

from pathlib import Path
import docx # for Word documents
import fitz # for PDFs
import os
from typing import Dict
import PyPDF2
from src.utils.rfp_extractors import extract_evaluation_criteria

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


import re
from src.utils.text_loader import load_text_file

def parse_rfp_from_file(filepath: str) -> dict:
    """
    Parses RFP file and extracts:
    - Full text
    - Section map (e.g., Background, Requirements, Criteria)
    - Evaluation criteria with weights and descriptions (if found)
    """
    full_text = load_report_text_from_file(filepath)
    
    # Step 1: Split sections using common RFP headers
    section_patterns = {
        "Background": r"(?:^|\n)(Background|Introduction)\s*[\n:-]",
        "Requirements": r"(?:^|\n)(Requirements|Business Needs|Scope of Work)\s*[\n:-]",
        "Evaluation Criteria": r"(?:^|\n)(Evaluation Criteria|Scoring Methodology|Proposal Evaluation)\s*[\n:-]",
        "Terms and Conditions": r"(?:^|\n)(Terms and Conditions|Contract Requirements)\s*[\n:-]",
    }

    sections = {}
    for name, pattern in section_patterns.items():
        match = re.search(pattern, full_text, flags=re.IGNORECASE)
        if match:
            start_idx = match.start()
            sections[name] = full_text[start_idx:]

    # Step 2: Try to extract evaluation criteria block
    criteria_block = sections.get("Evaluation Criteria", "")
    criteria = extract_evaluation_criteria(criteria_block)

    return {
        "full_text": full_text,
        "sections": sections,
        "criteria": criteria
    }


from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def preprocess_proposal_for_criteria_with_threshold(
    proposal_text: str,
    rfp_criteria: List[str],
    rfp_criterion_descriptions: Optional[Dict[str, str]] = None,
    score_threshold: float = 0.4
) -> Dict[str, str]:
    """
    Matches segments of proposal text to each RFP criterion using embedding similarity,
    returning only segments above a relevance threshold.
    """
    # Split proposal into paragraphs
    paragraphs = [p.strip() for p in proposal_text.split("\n") if p.strip()]
    para_embeddings = model.encode(paragraphs, convert_to_tensor=True)

    matched_sections = {}

    for criterion in rfp_criteria:
        query = rfp_criterion_descriptions.get(criterion, criterion) if rfp_criterion_descriptions else criterion
        query_embedding = model.encode(query, convert_to_tensor=True)

        # Compute similarity scores
        cosine_scores = util.pytorch_cos_sim(query_embedding, para_embeddings)[0]

        # Select all paragraphs above the threshold
        relevant_paragraphs = [
            para for para, score in zip(paragraphs, cosine_scores)
            if score.item() >= score_threshold
        ]

        # If nothing matched, fall back to top 1 best match
        if not relevant_paragraphs:
            top_idx = cosine_scores.argmax().item()
            relevant_paragraphs = [paragraphs[top_idx]]

        matched_sections[criterion] = "\n\n".join(relevant_paragraphs)

    return matched_sections
