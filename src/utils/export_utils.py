# export_utils.py – Report generation/export

import os
from models.openai_interface import call_openai_with_tracking
from markdown import markdown


def generate_final_summary(agent, model="gpt-3.5-turbo", temperature=0.7):
    """
    Generates a final summary for the client based on the agent's memory of section insights and cross-section observations.

    Purpose:
    This function constructs a prompt using the agent's memory of section insights and cross-section observations to generate a final summary for the client. It uses the OpenAI API to create a concise summary covering strengths, issues, and overall alignment with goals.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the memory data to be used for generating the summary.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.7.

    Workflow:
    1. Retrieves section notes and cross-section observations from the agent's memory.
    2. Constructs a prompt that includes the section insights and cross-section observations.
    3. Adds instructions to write a short, clear 4-6 sentence final summary covering strengths, issues, and overall alignment with goals.
    4. Creates a list of messages with the constructed prompt.
    5. Calls the OpenAI API with tracking using the call_openai_with_tracking function.
    6. If the API call is successful, returns the generated summary.
    7. If an exception occurs, returns a failure message with the exception details.

    Returns:
    str: The generated final summary or a failure message if the API call fails.
    """
    # Build a summary prompt using memory
    notes_by_section = agent.memory.get("section_notes", {})
    cross_section = agent.memory.get("cross_section_flags", [])

    prompt = "You are a senior consultant wrapping up your review of an IT strategy report.\n"
    prompt += "Use the following section insights and cross-section observations to write a final summary for the client.\n\n"

    for section, notes in notes_by_section.items():
        prompt += f"Section: {section}\n"
        for note in notes:
            prompt += f"- {note}\n"
        prompt += "\n"

    if cross_section:
        prompt += "Cross-Section Findings:\n"
        for a, b, obs in cross_section:
            prompt += f"- {a} vs. {b}: {obs}\n"
        prompt += "\n"

    # Include overall score summary
    if "section_scores" in agent.memory:
        prompt += "\nOverall Ratings:\n"
        for section, score_text in agent.memory["section_scores"].items():
            prompt += f"{section}:\n{score_text}\n\n"
            
    prompt += "Write a short, clear 4-6 sentence final summary covering strengths, issues, and overall alignment with goals."

    messages = [{"role": "user", "content": prompt}]
    
    try:
        return call_openai_with_tracking(messages, model=model, temperature=temperature).strip()
    except Exception as e:
        return f"⚠️ Failed to generate final summary: {str(e)}"


def export_report_to_markdown(agent, filename="consultant_ai_report.md"):
    """
    Exports a polished consulting report review in markdown format.
    Structure:
    1. Final Summary
    2. Top Issues
    3. Cross-Section Findings
    4. Missing Sections
    5. Section-by-Section Review (notes, ratings, fixes, confidence, rewrite)
    6. Citations
    """

    with open(filename, "w") as f:
        f.write("# 🧾 AI-Powered Consulting Report\n")

        # 1. Final Summary
        f.write("\n## 🧠 Final Summary\n")
        f.write(agent.memory.get("final_summary", "No summary generated.") + "\n")

        # 2. Top Issues
        if "top_issues" in agent.memory:
            f.write("\n## 🚨 Top 3 Issues\n")
            f.write(agent.memory["top_issues"] + "\n")

        # 3. Cross-Section Findings
        cross_flags = agent.memory.get("cross_section_flags", [])
        if cross_flags:
            f.write("\n## 🔀 Cross-Section Findings\n")
            for a, b, obs in cross_flags:
                f.write(f"- **{a} vs. {b}**: {obs}\n")

        # 4. Missing Sections
        if "highlight_missing" in agent.memory:
            f.write("\n## ❗ Missing Sections\n")
            f.write(agent.memory["highlight_missing"] + "\n")
        if "missing_analysis" in agent.memory:
            f.write("\n## 📌 Missing Sections Analysis\n")
            f.write(agent.memory["missing_analysis"] + "\n")

        # 5. Section Reviews
        write_section_insights(f, agent)

        # 6. Citations
        f.write("\n\n## 🔖 Citations & References\n")
        f.write(format_citations_block(agent) + "\n")

    print(f"✅ Markdown report saved as: {filename}")


def write_section_insights(f, agent):
    """
    Writes section insights, ratings, fixes, confidence levels, and improved sections to a markdown file.

    Purpose:
    This function iterates through the sections stored in the agent's memory and writes detailed insights for each section to a markdown file. It includes notes, ratings, fix recommendations, confidence levels, and optionally improved sections if available.

    Parameters:
    f (file object): The file object to write the markdown content to.

    Workflow:
    1. Writes a header for the section insights and ratings.
    2. Iterates through each section in the agent's memory.
    3. For each section:
        - Writes the section name as a subheader.
        - Writes the notes for the section, if available.
        - Writes the ratings for the section, if available, formatted as a score block.
        - Writes fix recommendations for the section, if available.
        - Writes the confidence level for the section, if available.
        - Writes the improved section content, if available, under a separate subheader.

    Returns:
    None
    """
    f.write("\n\n## 📚 Section Insights & Ratings\n")
    for section in agent.memory.get("section_notes", {}).keys():
        f.write(f"\n### 🔸 {section}\n")

        # Notes
        notes = agent.memory["section_notes"].get(section, [])
        if notes:
            f.write("**Notes:**\n")
            for note in notes:
                f.write(f"- {note}\n")

        # Ratings
        score_text = agent.memory.get("section_scores", {}).get(section, "")
        if score_text:
            f.write("\n**Ratings:**\n")
            f.write(f"{format_score_block(score_text)}\n")

        # Fixes
        fixes = agent.memory.get("section_fixes", {}).get(section, "")
        if fixes:
            f.write("\n**Fix Recommendations:**\n")
            f.write(f"{fixes}\n")

        # Confidence
        confidence = agent.memory.get("confidence_levels", {}).get(section, "")
        if confidence:
            f.write(f"\n**Confidence Level:** {confidence}/10\n")

        # Rewritten Section (optional)
        if section in agent.memory.get("section_upgrades", {}):
            upgrade = agent.memory["section_upgrades"][section]
            f.write("\n**💡 Improved Section:**\n")
            f.write(f"{upgrade['improved']}\n")

async def export_report_to_markdown_and_pdf(agent, markdown_file="consultant_ai_report.md", pdf_file="consultant_ai_report.pdf"):
    """
    Exports the consulting report review to both markdown and PDF formats.

    Purpose:
    This function generates a markdown file summarizing the consulting report review and then converts it to a PDF file. It ensures the output directory exists, exports the report to markdown, converts the markdown to HTML, and finally renders the HTML to a PDF file.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the memory data to be exported.
    markdown_file (str): The name of the markdown file to save. Default is "consultant_ai_report.md".
    pdf_file (str): The name of the PDF file to save. Default is "consultant_ai_report.pdf".

    Workflow:
    1. Ensures the output directory exists.
    2. Exports the report to a markdown file using the `export_report_to_markdown` function.
    3. Reads the markdown file and converts its content to HTML.
    4. Wraps the HTML content in a basic HTML page structure.
    5. Saves the HTML content to a temporary file.
    6. Uses Playwright to render the HTML file to a PDF.
    7. Handles any exceptions that occur during the PDF rendering process and prints appropriate messages.

    Asynchronous Workflow:
    1. Opens an async Playwright session.
    2. Launches a Chromium browser.
    3. Opens a new page in the browser.
    4. Navigates to the local HTML file.
    5. Generates a PDF from the HTML content.
    6. Closes the browser.
    7. Prints a success message if the PDF is saved successfully.
    
    Returns:
    None
    """
    # Ensure output directory exists
    output_dir = "../outputs/"
    os.makedirs(output_dir, exist_ok=True)
    markdown_file = os.path.join(output_dir, markdown_file)
    pdf_file = os.path.join(output_dir, pdf_file)
    
    # Step 1: Export to Markdown
    export_report_to_markdown(agent, filename=markdown_file)

    # Step 2: Convert to HTML
    with open(markdown_file, "r") as f:
        md_text = f.read()
    html_content = markdown(md_text)

    # Optional: wrap in basic HTML page
    full_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Consulting Report</title>
        <style>
            body {{ font-family: sans-serif; margin: 40px; line-height: 1.6; }}
            h1, h2, h3 {{ color: #003366; }}
            ul {{ margin-top: 0; }}
        </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """

    # Step 3: Save HTML and render to PDF
    temp_html_path = os.path.join(output_dir, "temp_report.html")
    with open(temp_html_path, "w") as f:
        f.write(full_html)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto("file://" + os.path.abspath(temp_html_path))
            await page.pdf(path=pdf_file, format="A4")
            await browser.close()
            print(f"✅ PDF report saved as: {pdf_file}")
    except Exception as e:
        print(f"⚠️ PDF export failed: {str(e)}")


def format_citations_block(agent):
    """
    Formats the citations and external references stored in the agent's memory into a markdown block.

    Purpose:
    This function retrieves the citations and external references from the agent's memory and formats them into a markdown string. Each section's citations are grouped and displayed with the query and result for easy readability.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the memory data with citations.

    Workflow:
    1. Initializes a list with a header for the citations section.
    2. Iterates through the citations stored in the agent's memory under the "citations" key.
    3. For each section, adds a subsection header with the section name.
    4. For each citation entry in the section:
       - Adds the query used to retrieve the citation.
       - Adds the result of the citation query.
    5. Joins the list of lines into a single markdown-formatted string.

    Returns:
    str: A markdown-formatted string containing the citations and external references grouped by section.
    """
    lines = ["## 📚 Citations & External References\n"]
    for section, entries in agent.memory.get("citations", {}).items():
        lines.append(f"### 🔹 {section}")
        for entry in entries:
            if entry["source"] == "arxiv":
                lines.append(f"- 🔍 *{entry['query']}* (from arXiv)\n{entry['result']}")
            elif entry["source"] == "serpapi":
                lines.append(f"- 🔍 *{entry['query']}* (from web)\n  📄 {entry['title']}\n  🔗 {entry['url']}\n  📌 {entry['snippet']}")
            else:
                lines.append(f"- ❓ Unknown citation source: {entry}")
    return "\n".join(lines)


def format_upgraded_sections(agent):
    """
    Formats the upgraded sections of a report with research enhancements into a markdown block.

    Purpose:
    This function retrieves the upgraded sections stored in the agent's memory, formats them into a markdown string, 
    and includes footnotes for any research-based improvements. It provides a clear and structured summary of 
    the enhancements made to each section.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the memory data 
                                  with upgraded sections and their corresponding footnotes.

    Workflow:
    1. Initializes a list with a header for the section improvements.
    2. Retrieves the upgraded sections from the agent's memory under the "section_upgrades" key.
    3. If no upgrades are found, appends a message indicating no upgrades were made and returns the formatted string.
    4. Iterates through each upgraded section:
       - Adds the section name as a subheader.
       - Appends the improved section text with footnotes.
       - If footnotes are available, appends a list of footnotes with the original text, improved text, and reason for the improvement.
    5. Joins the list of lines into a single markdown-formatted string.

    Returns:
    str: A markdown-formatted string containing the upgraded sections with research enhancements and footnotes.
    """
    lines = ["## ✨ Section Improvements with Research\n"]

    upgrades = agent.memory.get("section_upgrades", {})
    if not upgrades:
        lines.append("_No upgrades were made._")
        return "\n".join(lines)

    for section, data in upgrades.items():
        lines.append(f"\n### 🔹 {section}")
        lines.append("**Improved Section (with footnotes):**\n")
        lines.append(data['improved'].strip())

        if "footnotes" in data and data["footnotes"]:
            lines.append("\n**Footnotes:**\n")
            for idx, original, improved, reason in data["footnotes"]:
                lines.append(f"[^{idx}]: Originally: *{original.strip()}*")
                lines.append(f"      → *{improved.strip()}*")
                lines.append(f"      📚 Reason: {reason}\n")

    return "\n".join(lines)
