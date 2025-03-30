def inject_html_style(html_content: str) -> str:
    """
    Injects styling and font fallbacks into the HTML content.

    - Adds UTF-8 encoding if wrapping HTML is missing.
    - Supports raw markdown-to-html output.
    - Injects fallback emoji fonts.
    """
    style_block = """
    <meta charset="UTF-8">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans&display=swap');

    body {
        font-family: 'Noto Sans', 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif;
        font-size: 14px;
        line-height: 1.6;
        color: #333;
        padding: 20px;
        max-width: 800px;
        margin: auto;
    }
    h1, h2, h3 {
        font-weight: bold;
        margin-top: 1.5em;
    }
    pre, code {
        font-family: 'Courier New', monospace;
        background-color: #f4f4f4;
        padding: 4px;
        border-radius: 4px;
    }
    .tool-used {
        background-color: #f9f9f9;
        border-left: 4px solid #ccc;
        padding: 8px;
        margin: 6px 0;
    }
    </style>
    """

    # Case 1: HTML already has <head>
    if "<head>" in html_content:
        return html_content.replace("<head>", f"<head>{style_block}")
    
    # Case 2: HTML has <html> but no <head>
    elif "<html>" in html_content:
        return html_content.replace("<html>", f"<html><head>{style_block}</head>")

    # Case 3: Plain HTML fragment (from markdown)
    else:
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>{style_block}</head>
        <body>{html_content}</body>
        </html>
        """

