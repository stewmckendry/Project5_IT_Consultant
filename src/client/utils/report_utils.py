# utils/report_utils.py

import re
import difflib
from utils.tools import dispatch_tool_action, format_score_block, score_section, get_confidence_level, recommend_fixes, format_upgraded_sections, format_citations_block

canonical_section_map = {
    "Introduction": ["header", "intro", "project context", "introduction", "overview"],
    "Summary": ["summary", "executive summary"],
    "Goals & Objectives": ["goals", "objectives", "strategic priorities"],
    "Current State Assessment": ["current state", "as-is", "status quo"],
    "Future State": ["future state", "to-be", "vision", "target state"],
    "Key Recommendations": ["recommendations", "our recommendations", "next steps"],
    "Implementation Plan": ["implementation plan", "roadmap", "deployment", "schedule", "timeline", "phasing"],
    "Benefits": ["benefits", "value", "expected outcomes"],
    "Costs": ["costs", "financials", "budget", "investment"],
    "Resources": ["resources", "team structure", "staffing", "governance"],
    "Risks & Mitigations": ["risks", "mitigations", "risk mitigation"]
}

def map_section_to_canonical(label):
    lower_label = label.lower()
    for canonical, variants in canonical_section_map.items():
        for variant in variants:
            if variant in lower_label:
                return canonical
    all_variants = {v: k for k_list in canonical_section_map.values() for v in k_list}
    match = difflib.get_close_matches(lower_label, all_variants.keys(), n=1, cutoff=0.6)
    return all_variants.get(match[0]) if match else None

def split_report_into_sections(report_text):
    sections = {}
    lines = report_text.strip().split("\n")
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        elif line.endswith(":") and len(line.split()) <= 6:
            section_title = line.replace(":", "").strip()
            canonical = map_section_to_canonical(section_title) or section_title
            current_section = canonical
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)

    for k in sections:
        sections[k] = "\n".join(sections[k])

    return sections

def run_react_loop_check_withTool(agent, max_steps=5):
    for step_num in range(max_steps):
        messages = agent.build_react_prompt_withTools()
        from utils.openai_utils import call_openai_with_tracking
        response = call_openai_with_tracking(messages, model=agent.model, temperature=agent.temperature)

        try:
            lines = response.strip().split("\n")
            thought = next(line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("thought"))
            action = next(line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("action"))
            agent.tool_usage[action] = agent.tool_usage.get(action, 0) + 1
        except:
            break

        observation = dispatch_tool_action(agent, action, step_num)

        agent.memory["tool_history"].append((step_num, action, agent.section_name))
        agent.history.append({"thought": thought, "action": action, "observation": observation})

        if action == "summarize":
            break

    # Add section-level memory
    agent.memory["section_notes"][agent.section_name] = [s for s in [step['observation'] for step in agent.history[-3:]] if s]
    goals = agent.memory.get("Goals & Objectives") or None
    agent.memory.setdefault("section_scores", {})[agent.section_name] = score_section(agent.section_name, agent.section_text, goals_text=goals)
    agent.memory.setdefault("confidence_levels", {})[agent.section_name] = get_confidence_level(agent)
    agent.memory.setdefault("section_fixes", {})[agent.section_name] = recommend_fixes(agent)
    agent.memory.setdefault("debug_notes", {})[agent.section_name] = agent.history
    return agent.history

def export_report_to_markdown(agent, filename="consultant_ai_report.md"):
    with open(filename, "w") as f:
        f.write("# 🧾 AI-Powered Consulting Report\n\n")
        f.write("## Final Summary\n\n" + agent.memory.get("final_summary", "No summary generated.") + "\n\n")

        if "top_issues" in agent.memory:
            f.write("## Top 3 Issues\n" + agent.memory["top_issues"] + "\n")

        f.write("## Section Insights, Ratings, Fixes, and Confidence Levels\n")
        for section in agent.memory["section_notes"]:
            f.write(f"\n### {section}\n")
            for note in agent.memory["section_notes"].get(section, []):
                f.write(f"- {note}\n")
            if section in agent.memory["section_scores"]:
                f.write("\n**Ratings:**\n")
                f.write(format_score_block(agent.memory["section_scores"][section]) + "\n")
            if section in agent.memory["section_fixes"]:
                f.write("\n**Fix Recommendations:**\n" + agent.memory["section_fixes"][section] + "\n")
            if section in agent.memory["confidence_levels"]:
                f.write(f"\n**Confidence Level:** {agent.memory['confidence_levels'][section]}/10\n")

        f.write(format_citations_block(agent) + "\n")
        f.write("\n## Rewritten Sections\n" + format_upgraded_sections(agent))

        if agent.memory.get("cross_section_flags"):
            f.write("\n## Cross-Section Findings\n")
            for a, b, obs in agent.memory["cross_section_flags"]:
                f.write(f"- **{a} vs. {b}**: {obs}\n")

        if agent.memory.get("highlight_missing"):
            f.write("\n## Missing Sections Check\n" + agent.memory["highlight_missing"] + "\n")

        if agent.memory.get("missing_analysis"):
            f.write("\n## Analysis of Missing Sections\n" + agent.memory["missing_analysis"] + "\n")

    print(f"✅ Markdown report saved as: {filename}")