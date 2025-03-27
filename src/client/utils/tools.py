# utils/tools.py

import re
import difflib
from utils.openai_utils import call_openai_with_tracking

# Tool catalog (abbreviated)
# Tool catalog with descriptions, usage, and examples

tool_catalog = {
    "check_guideline": {
        "description": "Look up a best practice for a given topic",
        "usage": 'check_guideline["cloud security"]',
        "version": "v1.0",
        "examples": [
            "check_guideline[\"data governance\"]",
            "check_guideline[\"migration strategy\"]"
        ]
    },
    "keyword_match_in_section": {
        "description": "Check if a keyword appears in the current section",
        "usage": 'keyword_match_in_section["encryption"]',
        "version": "v1.0",
        "examples": [
            "keyword_match_in_section[\"stakeholders\"]"
        ]
    },
    "check_timeline_feasibility": {
        "description": "Check if a project timeline is realistic for migration",
        "usage": 'check_timeline_feasibility["12 weeks"]',
        "version": "v1.0",
        "examples": [
            "check_timeline_feasibility[\"3 months\"]"
        ]
    },
    "search_report": {
        "description": "Search the entire report for a concept or term",
        "usage": 'search_report["data governance"]',
        "version": "v1.0",
        "examples": [
            "search_report[\"Zero Trust\"]"
        ]
    },
    "ask_question": {
        "description": "Ask a clarifying question about the report",
        "usage": "ask_question",
        "version": "v1.0",
        "examples": ["ask_question"]
    },
    "flag_risk": {
        "description": "Flag a gap, issue, or concern in the section",
        "usage": "flag_risk",
        "version": "v1.0",
        "examples": ["flag_risk"]
    },
    "recommend_fix": {
        "description": "Suggest a specific improvement",
        "usage": "recommend_fix",
        "version": "v1.0",
        "examples": ["recommend_fix"]
    },
    "summarize": {
        "description": "Summarize your review and end the loop",
        "usage": "summarize",
        "version": "v1.0",
        "examples": ["summarize"]
    },
    "tool_help": {
        "description": "View descriptions, usage, and examples for available tools",
        "usage": "tool_help",
        "version": "v1.0",
        "examples": ["tool_help"]
    },
    "suggest_tool_for": {
        "description": "Ask which tool best supports a particular goal or intent",
        "usage": 'suggest_tool_for["goal or intent"]',
        "version": "v1.0",
        "examples": [
            'suggest_tool_for["check if encryption is included"]',
            'suggest_tool_for["evaluate feasibility of 12-week timeline"]'
        ]
    }, 
    "search_web": {
        "description": "Look up a concept, framework, or term on the web (DuckDuckGo)",
        "usage": 'search_web["Zero Trust model"]',
        "version": "v1.0",
        "examples": ['search_web["data mesh"]']
    },
    "check_for_jargon": {
        "description": "Identify jargon or overly technical terms that may need simplification",
        "usage": "check_for_jargon",
        "version": "v1.0",
        "examples": ["check_for_jargon"]
    },
    "generate_client_questions": {
        "description": "Generate clarifying or skeptical questions a client might ask about the section",
        "usage": "generate_client_questions",
        "version": "v1.0",
        "examples": ["generate_client_questions"]
    },
    "highlight_missing_sections": {
        "description": "Identify which expected sections are missing from the report",
        "usage": "highlight_missing_sections",
        "version": "v1.0",
        "examples": ["highlight_missing_sections"]
    },
    "check_alignment_with_goals": {
        "description": "Evaluate how well a report section aligns with the stated goals",
        "usage": 'check_alignment_with_goals["section_name"]',
        "version": "v1.0",
        "examples": ['check_alignment_with_goals["Key Recommendations"]']
    },
    "compare_with_other_section": {
        "description": "Compare two sections to identify overlaps, contradictions, or gaps",
        "usage": 'compare_with_other_section["sectionA", "sectionB"]',
        "version": "v1.0",
        "examples": [
            'compare_with_other_section["Key Recommendations", "Roadmap & Timeline"]',
            'compare_with_other_section["Future State Vision", "Technology Architecture"]'
        ]
    },
    "final_summary": {
        "description": "Generate a final client-facing summary based on insights gathered across all sections",
        "usage": "final_summary",
        "version": "v1.0",
        "examples": ["final_summary"]
    },
    "check_summary_support": {
        "description": "Check if a summary is supported by details in the rest of the report",
        "usage": 'check_summary_support["summary text"]',
        "version": "v1.0",
        "examples": ['check_summary_support["The report outlines benefits of cloud migration..."]']
    },
    "evaluate_smart_goals": {
        "description": "Evaluate whether stated goals follow the SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)",
        "usage": "evaluate_smart_goals",
        "version": "v1.0",
        "examples": ["evaluate_smart_goals"]
    },
    "check_recommendation_alignment": {
        "description": "Check whether the recommendations align with the goals of the report",
        "usage": 'check_recommendation_alignment["recommendation text"]',
        "version": "v1.0",
        "examples": ['check_recommendation_alignment["Modernize CRM and EHR with cloud-based tools"]']
    }, 
    "check_readability": {
        "description": "Evaluate the section’s readability and complexity using text statistics",
        "usage": "check_readability",
        "version": "v1.0",
        "examples": ["check_readability"]
    },
    "search_wikipedia": {
        "description": "Look up a concept on Wikipedia to gain factual context or definition",
        "usage": 'search_wikipedia["cloud computing"]',
        "version": "v1.0",
        "examples": ['search_wikipedia["Zero Trust"]', 'search_wikipedia["data governance"]']
    },
    "analyze_tone_textblob": {
        "description": "Analyze tone and subjectivity of the section using TextBlob",
        "usage": "analyze_tone_textblob",
        "version": "v1.0",
        "examples": ["analyze_tone_textblob"]
    },
    "search_serpapi": {
        "description": "Search the web in real time using Google (via SerpAPI)",
        "usage": 'search_serpapi["query here"]',
        "version": "v1.0",
        "examples": [
            'search_serpapi["cloud security trends 2024"]',
            'search_serpapi["real-world Zero Trust case studies"]'
        ]
    },
    "extract_named_entities": {
        "description": "Extract names of people, organizations, dates, and locations from the section",
        "usage": "extract_named_entities",
        "version": "v1.0",
        "examples": ["extract_named_entities"]
    },
    "analyze_math_question": {
        "description": "Ask a question involving math (ROI, budgets, timeframes) and get an explained answer",
        "usage": 'analyze_math_question["What is 20% of $120,000 over 3 years?"]',
        "version": "v1.0",
        "examples": [
            'analyze_math_question["If we save $500/month for 18 months, what’s the total savings?"]',
            'analyze_math_question["What’s 10% annual growth over 3 years?"]'
        ]
    },
    "search_arxiv": {
        "description": "Search academic papers on arXiv for technical or scientific topics",
        "usage": 'search_arxiv["FHIR interoperability"]',
        "version": "v1.0",
        "examples": [
            'search_arxiv["Zero Trust network security"]',
            'search_arxiv["AI for EHR classification"]'
        ]
    },
    "auto_check_for_academic_support": {
        "description": "Auto-evaluate if this section needs scientific citation. If yes, run arXiv search.",
        "usage": "auto_check_for_academic_support",
        "version": "v1.0",
        "examples": ["auto_check_for_academic_support"]
    },
    "should_cite": {
        "description": "Evaluate whether a statement should be supported by a citation",
        "usage": 'should_cite["statement text"]',
        "version": "v1.0",
        "examples": [
            'should_cite["Zero Trust improves security"]',
            'should_cite["Migrating in 12 weeks is realistic"]'
        ]
    },
    "auto_fill_gaps_with_research": {
        "description": "Expands vague or incomplete sections using search and reasoning",
        "usage": "auto_fill_gaps_with_research",
        "version": "v1.0",
        "examples": ["auto_fill_gaps_with_research"]
    }, 
    "upgrade_section_with_research": {
        "description": "Scans the section for weak or vague claims, determines if they need a citation, and improves them using external research.",
        "usage": "upgrade_section_with_research",
        "version": "v1.0",
        "examples": ["upgrade_section_with_research"]
    }
}


# Tool utilities
def build_tool_hints(agent):
    all_tools = list(tool_catalog.keys())
    return ", ".join(all_tools), all_tools

def format_tool_catalog_for_prompt(catalog):
    lines = ["\nAvailable tools:"]
    for name, meta in catalog.items():
        lines.append(f"- {name}: {meta['description']}")
    return "\n".join(lines) + "\n"

# Tool dispatcher
def dispatch_tool_action(agent, action, step_num):
    if action.startswith("check_guideline"):
        match = re.match(r'check_guideline\["(.+?)"\]', action)
        topic = match.group(1) if match else "unspecified"
        return f"✅ Best practice for {topic}: [Placeholder guideline]."

    elif action.startswith("keyword_match_in_section"):
        match = re.match(r'keyword_match_in_section\["(.+?)"\]', action)
        keyword = match.group(1)
        if keyword.lower() in agent.section_text.lower():
            return f"✅ The keyword '{keyword}' appears in the section."
        else:
            return f"❌ The keyword '{keyword}' was NOT found."

    elif action == "ask_question":
        return "Good question to ask the client for clarification."
    elif action == "flag_risk":
        return "This is a legitimate risk that should be addressed."
    elif action == "recommend_fix":
        return "The recommendation improves the section's clarity and compliance."
    elif action == "summarize":
        return "Review complete."
    elif action == "tool_help":
        return format_tool_catalog_for_prompt(tool_catalog)

    else:
        return "⚠️ Unrecognized or unsupported action."

# Example scoring

def score_section(section_name, section_text, goals_text=None, model="gpt-3.5-turbo"):
    prompt = f"Evaluate '{section_name}' for clarity, alignment with goals, and completeness."
    if goals_text:
        prompt += f"\n\nGoals:\n{goals_text}"
    prompt += f"\n\nSection:\n{section_text}\n\nFormat: Clarity: X/10 – Y\nAlignment: X/10 – Y\nCompleteness: X/10 – Y"
    messages = [{"role": "user", "content": prompt}]
    return call_openai_with_tracking(messages)

def format_score_block(score_text):
    def iconify(line):
        match = re.search(r"(\d+)/10", line)
        if not match:
            return line
        score = int(match.group(1))
        icon = "🟢" if score >= 8 else "🟡" if score >= 6 else "🔴"
        return f"{icon} {line}"
    return "\n".join([iconify(l) for l in score_text.splitlines()])

def get_confidence_level(agent):
    return min(10, 6 + len(agent.history))

def recommend_fixes(agent):
    return f"🔧 Suggested fix based on findings in section '{agent.section_name}'."

def format_upgraded_sections(agent):
    rewritten = agent.memory.get("upgraded_sections", {})
    lines = []
    for section, sentences in rewritten.items():
        lines.append(f"\n### {section}")
        for i, s in enumerate(sentences):
            lines.append(f"[^upgrade{i+1}] {s}")
    return "\n".join(lines)

def format_citations_block(agent):
    cits = agent.memory.get("citations", [])
    if not cits:
        return ""
    lines = ["\n## References"]
    for i, item in enumerate(cits):
        lines.append(f"[{i+1}] {item['source']} – {item['title']}")
    return "\n".join(lines)
