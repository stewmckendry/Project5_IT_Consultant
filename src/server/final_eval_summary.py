from src.models.openai_interface import call_openai_with_tracking

def generate_final_comparison_summary(all_vendor_evaluations, model="gpt-3.5-turbo"):
    """
    Generate a final client-facing comparison summary from multiple vendor evaluations.

    Includes:
    - Summary of each proposal
    - Differentiators
    - Key risks
    - Overall recommendation
    """
    import pandas as pd

    # Build a comparison table
    rows = []
    for eval_data in all_vendor_evaluations:
        vendor_name = eval_data["vendor_name"]
        row = {"Vendor": vendor_name}
        for r in eval_data["results"]:
            row[r["criterion"]] = r["proposal_score"]
        row["Overall"] = eval_data["overall_score"]
        rows.append(row)

    df = pd.DataFrame(rows)
    score_table_html = df.to_html(index=False, classes="score-table", border=0)

    # Build evaluation text block
    eval_blocks = []
    for eval in all_vendor_evaluations:
        eval_blocks.append(f"### {eval['vendor_name']}\n")
        for r in eval["results"]:
            eval_blocks.append(f"- **{r['criterion']}**: {r['proposal_score']}/10 – {r['proposal_explanation']}")
        eval_blocks.append(f"\n🧮 **Overall Score**: {eval['overall_score']}/10")
        eval_blocks.append(f"\n🧩 **SWOT Summary**:\n{eval['swot_summary']}")
    all_eval_text = "\n\n".join(eval_blocks)

    # Final LLM prompt
    prompt = f"""
You are a strategic advisor to a government client reviewing multiple vendor proposals for an IT system.

Below is a score comparison table, followed by detailed evaluation summaries and SWOT assessments for each vendor.

{score_table_html}

{all_eval_text}

Please write a final comparison summary that includes:
- A clear summary of how the proposals differ
- Key strengths and risks for each vendor
- Notable differentiators
- Final recommendation (with rationale)
- Anything the client should follow up on before final selection

Write in a professional, client-facing tone.
"""
    messages = [{"role": "user", "content": prompt}]
    comparison_summary = call_openai_with_tracking(messages, model=model)
    return comparison_summary, score_table_html
