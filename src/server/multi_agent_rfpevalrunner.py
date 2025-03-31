from pathlib import Path
import pandas as pd
from typing import Dict, List
from src.server.proposal_eval import evaluate_proposal
from src.utils.export_utils import export_proposal_report, save_markdown_and_pdf
from src.server.final_eval_summary import generate_final_comparison_summary
from src.utils.file_loader import load_report_text_from_file, parse_rfp_from_file

def run_multi_proposal_evaluation(proposals: Dict[str, str], rfp_file: str = None, rfp_criteria: List[str] = None, model="gpt-3.5-turbo") -> tuple:
    """
    Runs multi-agent evaluation for multiple proposals against common RFP criteria.
    
    Parameters:
        proposals (dict): Dictionary of vendor_name: proposal_text
        rfp_criteria (list): List of evaluation criteria
        model (str): LLM model name to use

    Returns:
        results_dict: {vendor_name: full evaluation output}
        summary_markdown: markdown comparison summary
        score_table: DataFrame with scores per criterion per vendor
    """
    # Step 1: Extract criteria if needed
    if rfp_file:
        print(f"📄 Loading RFP from {rfp_file}...")
        rfp_text = load_report_text_from_file(rfp_file)
        rfp_criteria = parse_rfp_from_text(rfp_text)
        print(f"✅ Extracted RFP criteria: {rfp_criteria}")

    assert rfp_criteria is not None and len(rfp_criteria) > 0, "No RFP criteria provided or extracted."


    # Define output directory
    project_root = Path.cwd().parent
    outputs_dir = project_root / "outputs" / "proposal_eval_reports"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    all_vendor_evaluations = []

    for vendor_name, proposal_text in proposals.items():
        print(f"\n🚀 Evaluating {vendor_name}...")

        # Step 1: Evaluate proposal
        results, overall_score, swot_summary = evaluate_proposal(proposal_text, rfp_criteria, model=model)
        print(f"✅ {vendor_name} evaluation complete.")

        # Step 2: Save full proposal report (Markdown + HTML + PDF)
        export_proposal_report(vendor_name, results, overall_score, swot_summary, output_dir=outputs_dir)
        print(f"✅ {vendor_name} evaluation report saved.")

        # Step 3: Add to combined results
        all_vendor_evaluations.append({
            "vendor_name": vendor_name,
            "results": results,
            "overall_score": overall_score,
            "swot_summary": swot_summary
        })

    # Step 4: Generate final LLM summary
    print("\n🧠 Generating final comparison summary...")
    final_summary_text, score_table_md = generate_final_comparison_summary(all_vendor_evaluations, model=model)

    # Step 5: Save final summary
    save_markdown_and_pdf(
        markdown_text=final_summary_text,
        additional_md=score_table_md,
        filename="final_summary_report",
        output_dir="outputs/proposal_eval_reports"
    )
    print("✅ Final summary report saved.")

    return all_vendor_evaluations, final_summary_text