def inject_html_style(html_content: str, for_pdf: bool = False) -> str:
    """
    Wraps HTML content with appropriate CSS and UTF-8 encoding based on the rendering target (HTML or PDF).
    """
    meta_charset = '<meta charset="UTF-8">'

    if for_pdf:
        # PDF-safe: Avoid emoji fonts to prevent rendering errors
        css = """
        <style>
        body {
            font-family: 'Noto Sans', sans-serif;
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
        .score-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1em;
        }
        .score-table th, .score-table td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        .score-table th {
            background-color: #f2f2f2;
            text-align: left;
        }

        @media print {
            h2 {
                page-break-before: always;
            }
            .no-page-break {
                page-break-inside: avoid;
            }
        }
        </style>
        """
    else:
        # Full HTML styling with emoji-friendly fonts
        css = """
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Noto+Color+Emoji" rel="stylesheet">
        <style>
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
        .score-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1em;
        }
        .score-table th, .score-table td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        .score-table th {
            background-color: #f2f2f2;
            text-align: left;
        }

        @media print {
            h2 {
                page-break-before: always;
            }
            .no-page-break {
                page-break-inside: avoid;
            }
        }
        </style>
        """

    return f"<!DOCTYPE html><html><head>{meta_charset}{css}</head><body>{html_content}</body></html>"
