from pathlib import Path
import os
from typing import Dict, List
from datetime import datetime
from src.server.proposal_eval import evaluate_proposal
from src.utils.export_utils import export_proposal_report, save_markdown_and_pdf
from src.server.final_eval_summary import generate_final_comparison_summary
from src.utils.file_loader import parse_rfp_from_file
from src.utils.logging_utils import log_phase, log_result, reset_dedup_stats
from src.utils.logging_reports import finalize_evaluation_run

def run_multi_proposal_evaluation(proposals: Dict[str, str], rfp_file: str = None, rfp_criteria: List[str] = None, model="gpt-3.5-turbo") -> dict:
    """
    Run evaluations for multiple vendor proposals against RFP criteria.
    Args:
        proposals (Dict[str, str]): Dictionary of vendor names and their proposal texts.
        rfp_file (str): Path to the RFP file.
        rfp_criteria (List[str]): List of RFP criteria.
        model (str): Model name for evaluation.
    Returns:
        dict: Dictionary containing evaluations, final summary text, and file paths.
    """
    # Load RFP criteria from file if provided
    if rfp_file:
        log_phase(f"📄 Loading RFP from {rfp_file}...")
        rfp_parsed = parse_rfp_from_file(rfp_file)
        rfp_criteria = rfp_parsed["criteria"]
        log_phase(f"✅ Extracted RFP criteria: {rfp_criteria}")
        rfp_info = {
            "criteria": rfp_criteria,
            "path": rfp_file,
        }
    assert rfp_criteria, "No RFP criteria provided or extracted."

    # Prepare output folders
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_output = os.getenv("OUTPUT_DIR", "outputs")
    outputs_dir = Path(base_output) / "proposal_eval_reports" / run_id  
    outputs_dir.mkdir(parents=True, exist_ok=True)

    all_vendor_evaluations = []
    proposal_reports = {}
    reset_dedup_stats()

    for vendor_name, proposal_text in sorted(proposals.items()):
        log_phase(f"\n🚀 Evaluating {vendor_name}...")
        executed_tools_global = set()
        results, overall_score, swot_summary = evaluate_proposal(
            proposal_text, rfp_criteria, model=model, executed_tools_global=executed_tools_global
        )
        file_paths = export_proposal_report(
            vendor_name, results, overall_score, swot_summary, output_dir=outputs_dir
        )
        proposal_reports[vendor_name] = file_paths
        all_vendor_evaluations.append({
            "vendor_name": vendor_name,
            "results": results,
            "overall_score": overall_score,
            "swot_summary": swot_summary
        })

    final_summary_text, score_table_md = generate_final_comparison_summary(all_vendor_evaluations, model=model)
    final_summary_paths = save_markdown_and_pdf(
        markdown_text=final_summary_text,
        additional_md=score_table_md,
        filename="final_summary_report",
        output_dir=outputs_dir
    )

    # Log analytics report
    all_results = [r for vendor in all_vendor_evaluations for r in vendor["results"]]
    log_report_path= finalize_evaluation_run(results=all_results)

    return {
        "run_id": run_id,
        "rfp_info": rfp_info,
        "evaluations": all_vendor_evaluations,
        "final_summary_text": final_summary_text,
        "file_paths": {
            "proposal_reports": proposal_reports,
            "final_summary": final_summary_paths,
            "log_summary": log_report_path
        }
    }
