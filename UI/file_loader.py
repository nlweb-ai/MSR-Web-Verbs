"""File loading and tab management utilities"""
import tkinter as tk
from tkinter import scrolledtext
import os
import fnmatch
import re
from markdown_renderer import render_markdown, configure_markdown_tags


def load_files_as_tabs(app, notebook, file_pattern):
    """Load filtered files from tasks directory as tabs
    
    Args:
        app: The ChatApp instance (for accessing workspace_path, task_name)
        notebook: The notebook widget to add tabs to
        file_pattern: File pattern to match (e.g., 'task-*.md' or 'strategy-*.md')
    """
    # Determine if this is for strategies (read-only renderer) or tasks (editable)
    is_strategy = file_pattern.startswith("strategy-")
    
    # Get the tasks directory path
    tasks_dir = os.path.join(app.workspace_path, "tasks", app.task_name)
    
    if not os.path.exists(tasks_dir):
        # If directory doesn't exist, just return without creating tabs
        return
    
    # Get all files in the directory that match the pattern
    all_files = [f for f in os.listdir(tasks_dir) if os.path.isfile(os.path.join(tasks_dir, f))]
    files = sorted([f for f in all_files if fnmatch.fnmatch(f, file_pattern)])
    
    if not files:
        # If no files, just return without creating tabs
        return
    
    # Create a tab for each file
    for filename in files:
        file_path = os.path.join(tasks_dir, filename)
        
        # Extract number from filename and create tab label (e.g., "task-0001.md" -> "V0001")
        match = re.search(r'-(\d+)', filename)
        if match:
            tab_label = f"V{match.group(1)}"
        else:
            tab_label = filename  # fallback to filename if no number found
        
        # Create a frame for this tab
        tab_frame = tk.Frame(notebook)
        
        if is_strategy:
            # For strategies: create read-only text widget (renderer)
            text_widget = scrolledtext.ScrolledText(
                tab_frame,
                wrap=tk.WORD,
                font=("Consolas", 12),
                bg="#f5f5f5",
                state=tk.DISABLED
            )
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Configure tags for markdown formatting
            configure_markdown_tags(text_widget)
        else:
            # For tasks: create editable text widget
            text_widget = scrolledtext.ScrolledText(
                tab_frame,
                wrap=tk.WORD,
                font=("Consolas", 12),
                bg="white"
            )
            text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Read and display file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if is_strategy:
                    # Enable temporarily to insert content with markdown rendering
                    text_widget.config(state=tk.NORMAL)
                    render_markdown(text_widget, content)
                    # Disable again to make it read-only
                    text_widget.config(state=tk.DISABLED)
                else:
                    text_widget.insert(tk.END, content)
        except Exception as e:
            if is_strategy:
                text_widget.config(state=tk.NORMAL)
            text_widget.insert(tk.END, f"Error loading file: {e}")
            if is_strategy:
                text_widget.config(state=tk.DISABLED)
        
        # Add the tab to the notebook with the V* label
        notebook.add(tab_frame, text=tab_label)
    
    # Select the last tab (highest version) after loading all tabs
    if notebook.index('end') > 0:
        notebook.select(notebook.index('end') - 1)


def find_text_widget(widget):
    """Recursively find a Text widget within a widget hierarchy
    
    ScrolledText is actually a Frame containing a Text widget, so we need
    to search recursively to find the actual Text widget.
    
    Args:
        widget: The widget to search in
        
    Returns:
        The Text widget if found, None otherwise
    """
    for child in widget.winfo_children():
        if isinstance(child, tk.Text):
            return child
        # Recursively search in child widgets
        found = find_text_widget(child)
        if found:
            return found
    return None


def load_single_file_as_tab(app, notebook, file_path, tab_label):
    """Load a single file as a new tab in a notebook
    
    Args:
        app: The ChatApp instance
        notebook: The notebook widget to add the tab to
        file_path: Full path to the file to load
        tab_label: Label for the tab (e.g., "V0001")
    """
    # Determine if this is a strategy tab (strategies are read-only)
    is_strategy = 'strategy' in os.path.basename(file_path).lower()
    
    # Create a frame for this tab
    tab_frame = tk.Frame(notebook)
    
    if is_strategy:
        # For strategies: create read-only text widget (renderer)
        text_widget = scrolledtext.ScrolledText(
            tab_frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg="#f5f5f5",
            state=tk.DISABLED
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for markdown formatting
        configure_markdown_tags(text_widget)
    else:
        # For tasks: create editable text widget
        text_widget = scrolledtext.ScrolledText(
            tab_frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg="white"
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Read and display file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if is_strategy:
                # Enable temporarily to insert content with markdown rendering
                text_widget.config(state=tk.NORMAL)
                render_markdown(text_widget, content)
                # Disable again to make it read-only
                text_widget.config(state=tk.DISABLED)
            else:
                text_widget.insert(tk.END, content)
    except Exception as e:
        if is_strategy:
            text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, f"Error loading file: {e}")
        if is_strategy:
            text_widget.config(state=tk.DISABLED)
    
    # Add the tab to the notebook with the provided label
    notebook.add(tab_frame, text=tab_label)
