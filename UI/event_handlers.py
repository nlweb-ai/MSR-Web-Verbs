"""Event handlers for the chat application"""
import re


def update_highest_version(notebook, attr_name):
    """Update the highest version number from notebook tabs
    
    Args:
        notebook: The notebook widget to scan
        attr_name: Name of attribute to store result ('highest_task_version' or 'highest_strategy_version')
        
    Returns:
        The highest version number found, or None
    """
    highest_version = None
    tabs = notebook.tabs()
    
    if tabs:
        # Extract version numbers from tab labels
        versions = []
        for tab in tabs:
            tab_text = notebook.tab(tab, "text")
            match = re.search(r'V(\d+)', tab_text)
            if match:
                versions.append(int(match.group(1)))
        
        if versions:
            highest_version = max(versions)
    
    return highest_version


def handle_task_tab_changed(app, event=None):
    """Handle task tab change to show/hide buttons
    
    Args:
        app: The ChatApp instance
        event: The event object (optional)
    """
    if not hasattr(app, 'highest_task_version') or app.highest_task_version is None:
        return
    
    # Get current tab
    current_tab = app.tasks_notebook.select()
    if current_tab:
        tab_text = app.tasks_notebook.tab(current_tab, "text")
        
        # Check if this is the highest version
        match = re.search(r'V(\d+)', tab_text)
        if match and int(match.group(1)) == app.highest_task_version:
            # Show button
            app.generate_strategy_button.pack(side='left')
        else:
            # Hide button
            app.generate_strategy_button.pack_forget()


def handle_strategy_tab_changed(app, event=None):
    """Handle strategy tab change to show/hide Execute button
    
    Args:
        app: The ChatApp instance
        event: The event object (optional)
    """
    if not hasattr(app, 'highest_strategy_version') or app.highest_strategy_version is None:
        return
    
    # Get current tab
    current_tab = app.strategies_notebook.select()
    if current_tab:
        tab_text = app.strategies_notebook.tab(current_tab, "text")
        
        # Check if this is the highest version
        match = re.search(r'V(\d+)', tab_text)
        if match and int(match.group(1)) == app.highest_strategy_version:
            # Show button
            app.execute_button.pack(side='left')
        else:
            # Hide button
            app.execute_button.pack_forget()
