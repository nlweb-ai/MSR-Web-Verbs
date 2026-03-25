"""Markdown rendering utilities for text widgets"""
import tkinter as tk
import re


def render_markdown(text_widget, content):
    """Render markdown content with basic formatting in a text widget
    
    Args:
        text_widget: The Text widget to render markdown into
        content: The markdown content string to render
    """
    lines = content.split('\n')
    in_code_block = False
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            text_widget.insert(tk.END, '\n')
            i += 1
            continue
        
        if in_code_block:
            text_widget.insert(tk.END, line + '\n', "code_block")
            i += 1
            continue
        
        # Check for table: line contains | and next line is a separator row
        if '|' in line and i + 1 < len(lines) and re.match(r'^\s*\|?[\s\-:|]+\|', lines[i + 1]):
            # Collect all contiguous table rows
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            _render_table(text_widget, table_lines)
            continue
        
        # Headers
        if line.startswith('### '):
            text_widget.insert(tk.END, line[4:] + '\n', "h3")
        elif line.startswith('## '):
            text_widget.insert(tk.END, line[3:] + '\n', "h2")
        elif line.startswith('# '):
            text_widget.insert(tk.END, line[2:] + '\n', "h1")
        else:
            # Process inline formatting (bold, italic, code)
            render_inline_markdown(text_widget, line)
            text_widget.insert(tk.END, '\n')
        
        i += 1


def _parse_table_row(line):
    """Split a markdown table row into cell strings."""
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [cell.strip() for cell in line.split('|')]


def _render_table(text_widget, table_lines):
    """Render a markdown table with aligned columns."""
    # Parse rows, skip separator row(s)
    rows = []
    for tl in table_lines:
        stripped = tl.strip()
        if re.match(r'^\|?[\s\-:|]+\|?$', stripped):
            continue  # separator row
        rows.append(_parse_table_row(tl))
    
    if not rows:
        return
    
    # Determine column count and widths
    num_cols = max(len(r) for r in rows)
    col_widths = [0] * num_cols
    for row in rows:
        for ci, cell in enumerate(row):
            if ci < num_cols:
                col_widths[ci] = max(col_widths[ci], len(cell))
    
    # Render header
    header = rows[0]
    header_str = '  '.join(
        (header[ci] if ci < len(header) else '').ljust(col_widths[ci])
        for ci in range(num_cols)
    )
    text_widget.insert(tk.END, header_str + '\n', "table_header")
    
    # Render separator
    sep_str = '  '.join('─' * col_widths[ci] for ci in range(num_cols))
    text_widget.insert(tk.END, sep_str + '\n', "table_sep")
    
    # Render data rows
    for row in rows[1:]:
        row_str = '  '.join(
            (row[ci] if ci < len(row) else '').ljust(col_widths[ci])
            for ci in range(num_cols)
        )
        text_widget.insert(tk.END, row_str + '\n', "table_row")
    
    text_widget.insert(tk.END, '\n')


def render_inline_markdown(text_widget, line):
    """Render inline markdown formatting (bold, italic, code)
    
    Args:
        text_widget: The Text widget to render into
        line: The line of text to process for inline formatting
    """
    if not line:
        return
    
    # Pattern to match inline code, bold, and italic
    # Order matters: check code first, then bold, then italic
    pattern = r'(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*]+\*)'
    last_end = 0
    
    for match in re.finditer(pattern, line):
        # Insert text before the match
        if match.start() > last_end:
            text_widget.insert(tk.END, line[last_end:match.start()])
        
        matched_text = match.group(0)
        if matched_text.startswith('`') and matched_text.endswith('`'):
            # Inline code
            text_widget.insert(tk.END, matched_text[1:-1], "code")
        elif matched_text.startswith('**') and matched_text.endswith('**'):
            # Bold
            text_widget.insert(tk.END, matched_text[2:-2], "bold")
        elif matched_text.startswith('*') and matched_text.endswith('*'):
            # Italic
            text_widget.insert(tk.END, matched_text[1:-1], "italic")
        
        last_end = match.end()
    
    # Insert remaining text
    if last_end < len(line):
        text_widget.insert(tk.END, line[last_end:])


def configure_markdown_tags(text_widget):
    """Configure text tags for markdown formatting
    
    Args:
        text_widget: The Text widget to configure tags for
    """
    text_widget.tag_configure("h1", font=("Arial", 18, "bold"), spacing3=10)
    text_widget.tag_configure("h2", font=("Arial", 16, "bold"), spacing3=8)
    text_widget.tag_configure("h3", font=("Arial", 14, "bold"), spacing3=6)
    text_widget.tag_configure("bold", font=("Consolas", 12, "bold"))
    text_widget.tag_configure("italic", font=("Consolas", 12, "italic"))
    text_widget.tag_configure("code", font=("Courier", 12), background="#e0e0e0")
    text_widget.tag_configure("code_block", font=("Courier", 12), background="#e0e0e0", lmargin1=20, lmargin2=20)
    text_widget.tag_configure("table_header", font=("Consolas", 11, "bold"), background="#e8e8e8", lmargin1=10, lmargin2=10)
    text_widget.tag_configure("table_sep", font=("Consolas", 11), foreground="#999999", lmargin1=10, lmargin2=10)
    text_widget.tag_configure("table_row", font=("Consolas", 11), lmargin1=10, lmargin2=10)
