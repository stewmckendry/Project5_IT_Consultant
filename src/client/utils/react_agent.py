import os
from utils.file_utils import extract_text_from_file, save_markdown_to_file, convert_markdown_to_pdf
from utils.section_splitter import split_report_into_sections
from utils.agent_runner import run_react_loop_check_withTool
from utils.report_summarizer import generate_final_summary, extract_top_issues, format_citations_block, format_upgraded_sections, highlight_missing_sections, analyze_missing_section_importance
from utils.section_scoring import score_section, get_confidence_level, recommend_fixes
from utils.memory import ReActConsultantAgent
from utils.formatting import export_report_to_markdown


def process_report_and_generate_summary(file_path, user_notes=""):
    # Step 1: Extract text from file
    raw_text = extract_text_from_file(file_path)

    # Step 2: Pre-process into sections
    report_sections = split_report_into_sections(raw_text)

    # Step 3: Create agent to hold memory across sections
    agent = ReActConsultantAgent(section_name="Full Report", section_text="")

    # Step 4: Loop through each report section and run ReAct
    for section_name, section_text in report_sections.items():
        agent.section_name = section_name
        agent.section_text = section_text
        agent.report_sections = report_sections  # share globally
        run_react_loop_check_withTool(agent, max_steps=5)

    # Step 5: Add insights to memory
    agent.memory["final_summary"] = generate_final_summary(agent)
    agent.memory["top_issues"] = extract_top_issues(agent)
    agent.memory["highlight_missing"] = highlight_missing_sections(report_sections)
    agent.memory["missing_analysis"] = analyze_missing_section_importance(agent.memory["highlight_missing"], report_sections)

    # Step 6: Export markdown and PDF
    output_md_path = "output/consultant_ai_report.md"
    output_pdf_path = "output/consultant_ai_report.pdf"
    os.makedirs("output", exist_ok=True)
    export_report_to_markdown(agent, filename=output_md_path)
    convert_markdown_to_pdf(output_md_path, output_pdf_path)

    return output_md_path, output_pdf_path
