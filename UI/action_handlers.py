"""Action handlers for button clicks and user interactions"""
import os
import re
import tkinter as tk
from copilot import copilot_stream


def submit_message(app):
    """Handle message submission
    
    Args:
        app: The ChatApp instance
    """
    message = app.input_box.get().strip()
    
    if message:
        # Enable chat display to insert user's prompt
        app.chat_display.config(state=tk.NORMAL)
        
        # Append user's prompt to chat display
        app.chat_display.insert(tk.END, f"User: {message}\n", "user")
        
        # Auto-scroll to the bottom
        app.chat_display.see(tk.END)
        
        # Disable chat display temporarily
        app.chat_display.config(state=tk.DISABLED)
        
        # Update the UI to show the message
        app.root.update_idletasks()
        
        # Enable chat display to insert response
        app.chat_display.config(state=tk.NORMAL)
        
        # Insert copilot label
        app.chat_display.insert(tk.END, "Copilot: ", "copilot")
        
        # Get existing conversation as context
        conversation_history = app.chat_display.get("1.0", tk.END).strip()
        
        # Prepare message with conversation context
        if conversation_history:
            message_with_context = f"{message}.  \n*********  Here is the previous conversation for context: {conversation_history}\n ***** \n\n\n Also, read the files in the current working directory. Do ask whether you should read the directory. Just read it. \n*********"
        else:
            message_with_context = message
        #print (f"message_with_context: {message_with_context}\n\n")
        # Stream copilot responses as they arrive
        response_received = False
        for chunk in copilot_stream(message_with_context, app.case_dir):
            if chunk:
                response_received = True
                app.chat_display.insert(tk.END, "\n" + chunk, "copilot")
                app.chat_display.see(tk.END)
                app.root.update_idletasks()  # Force UI update for each chunk
        
        if not response_received:
            app.chat_display.insert(tk.END, "No response or error occurred.", "error")
        
        # Add spacing after response
        app.chat_display.insert(tk.END, "\n\n")
        
        # Auto-scroll to the bottom
        app.chat_display.see(tk.END)
        
        # Disable chat display to prevent manual editing
        app.chat_display.config(state=tk.DISABLED)
        
        # Clear the input box
        app.input_box.delete(0, tk.END)
        
        # Set focus back to input box
        app.input_box.focus_set()


def open_task(app):
    """Handle opening a new task by reloading tabs with the new task name
    
    Args:
        app: The ChatApp instance
    """
    from file_loader import load_files_as_tabs
    from event_handlers import update_highest_version, handle_task_tab_changed, handle_strategy_tab_changed
    
    new_task_name = app.task_name_input.get().strip()
    
    if new_task_name:
        # Save the task name to cache.txt
        cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache.txt")
        with open(cache_file, 'w') as f:
            f.write(new_task_name)
    
    if new_task_name and new_task_name != app.task_name:
        # Update task name
        app.task_name = new_task_name
        app.case_dir = os.path.join(app.workspace_path, "tasks", app.task_name)
        
        # Clear existing tabs
        for tab in app.tasks_notebook.tabs():
            app.tasks_notebook.forget(tab)
        for tab in app.strategies_notebook.tabs():
            app.strategies_notebook.forget(tab)
        
        # Reload tabs with new task name
        load_files_as_tabs(app, app.tasks_notebook, "task-*.md")
        load_files_as_tabs(app, app.strategies_notebook, "strategy-*.md")
        
        # Update highest task version and button visibility
        app.highest_task_version = update_highest_version(app.tasks_notebook, 'highest_task_version')
        app.highest_strategy_version = update_highest_version(app.strategies_notebook, 'highest_strategy_version')
        handle_task_tab_changed(app)
        handle_strategy_tab_changed(app)


def generate_strategy(app):
    """Handle Generate Strategy button click
    
    Args:
        app: The ChatApp instance
    """
    from file_loader import find_text_widget
    
    # Get the current task tab
    current_tab = app.tasks_notebook.select()
    if not current_tab:
        return
    
    # Get the tab text (e.g., "V0004")
    tab_text = app.tasks_notebook.tab(current_tab, "text")
    
    # Extract the task number
    match = re.search(r'V(\d+)', tab_text)
    if match:
        task_number = match.group(1)
        
        # Get the task content from the current tab
        current_tab_index = app.tasks_notebook.index(current_tab)
        tab_frame = app.tasks_notebook.nametowidget(current_tab)
        
        text_widget = find_text_widget(tab_frame)
        
        if not text_widget:
            print("Error: Could not find text widget in tab")
            return
        
        task_content = text_widget.get("1.0", tk.END).strip()
        
        # Save the task content to disk before generating code
        task_file = os.path.join(app.case_dir, f"task-{task_number}.md")
        os.makedirs(os.path.dirname(task_file), exist_ok=True)
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(task_content)
        
        # Construct the output file path
        task_name_clean = app.task_name.replace("-", "_")
        java_class_name = f"Code_{task_name_clean}_{task_number}"
        output_file = os.path.join(app.workspace_path, "generated_solutions", app.task_name, f"{java_class_name}.java")
        
        # Display message in chat window
        app.chat_display.config(state=tk.NORMAL)
        app.chat_display.insert(tk.END, f"I will create the file {output_file}\n\n", "copilot")
        app.chat_display.insert(tk.END, "Generating Java code...\n", "copilot")
        app.chat_display.see(tk.END)
        app.chat_display.config(state=tk.DISABLED)
        app.root.update_idletasks()
        
        # Create prompt for copilot by reading template and replacing placeholders
        template_path = os.path.join(os.path.dirname(__file__), "prompt_refine_code_template.txt")
        with open(template_path, 'r', encoding='utf-8') as f:
            prompt = f.read().replace("{task_name}", app.task_name).replace("{java_class_name}", java_class_name)
        
        # Create popup window for displaying generated code
        popup = tk.Toplevel(app.root)
        popup.title("Scratchpad")
        popup.geometry("800x600")
        
        # Create text widget with scrollbar for code display
        code_frame = tk.Frame(popup)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        code_scrollbar = tk.Scrollbar(code_frame)
        code_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        code_display = tk.Text(code_frame, wrap=tk.NONE, yscrollcommand=code_scrollbar.set, font=("Courier", 12), fg="green")
        code_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        code_scrollbar.config(command=code_display.yview)
        code_display.config(state=tk.NORMAL)
        
        # Make popup visible and update
        popup.update()
        
        # Stream copilot response and collect the generated code
        generated_code = []
        for chunk in copilot_stream(prompt, app.workspace_path):
            if chunk:
                generated_code.append(chunk)
                code_display.insert(tk.END, chunk + "\n")
                code_display.see(tk.END)
                code_display.update_idletasks()
                popup.update()
        
        code_display.config(state=tk.DISABLED)
        
        # Close the popup window
        popup.destroy()
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        # Write the generated code to file
        full_code = "\n".join(generated_code)
        
        # Extract content between markdown code fences if present
        full_code = full_code.strip()
        
        # Find the first occurrence of ``` (with optional language identifier)
        start_marker_match = re.search(r'^\s*```(?:java|[a-z]*)\s*$', full_code, re.MULTILINE)
        if start_marker_match:
            start_pos = start_marker_match.end()
            # Skip any whitespace/newline after the opening marker
            while start_pos < len(full_code) and full_code[start_pos] in '\r\n':
                start_pos += 1
            
            # Find the closing ``` after the start marker
            end_marker_match = re.search(r'^\s*```\s*$', full_code[start_pos:], re.MULTILINE)
            if end_marker_match:
                # Extract content between markers
                full_code = full_code[start_pos:start_pos + end_marker_match.start()]
        
        full_code = full_code.strip()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_code)
        
        app.chat_display.config(state=tk.NORMAL)
        app.chat_display.insert(tk.END, f"\n\nCode successfully written to {output_file}\n\n", "copilot")
        app.chat_display.see(tk.END)
        app.chat_display.config(state=tk.DISABLED)
        
        # Generate strategy summary from the automate() function
        app.chat_display.config(state=tk.NORMAL)
        app.chat_display.insert(tk.END, "Generating strategy summary...\n", "copilot")
        app.chat_display.see(tk.END)
        app.chat_display.config(state=tk.DISABLED)
        app.root.update_idletasks()
        
        # Extract the automate() function from the generated code
        automate_match = re.search(r'static\s+JsonObject\s+automate\s*\([^)]*\)\s*\{', full_code, re.DOTALL)
        if automate_match:
            # Find the matching closing brace
            start_pos = automate_match.start()
            brace_count = 0
            in_function = False
            end_pos = start_pos
            
            for i in range(start_pos, len(full_code)):
                if full_code[i] == '{':
                    brace_count += 1
                    in_function = True
                elif full_code[i] == '}':
                    brace_count -= 1
                    if in_function and brace_count == 0:
                        end_pos = i + 1
                        break
            
            automate_function = full_code[start_pos:end_pos]
            
            # Create prompt to summarize the automate function by reading template
            template_path = os.path.join(os.path.dirname(__file__), "prompt_summarize_strategy_template.txt")
            with open(template_path, 'r', encoding='utf-8') as f:
                summary_prompt = f.read().replace("{automate_function}", automate_function)
            
            # Create popup window for displaying strategy summary generation
            popup = tk.Toplevel(app.root)
            popup.title("Strategy Summary Generation")
            popup.geometry("800x600")
            
            # Create text widget with scrollbar for summary display
            summary_frame = tk.Frame(popup)
            summary_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            summary_scrollbar = tk.Scrollbar(summary_frame)
            summary_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            summary_display = tk.Text(summary_frame, wrap=tk.WORD, yscrollcommand=summary_scrollbar.set, font=("Courier", 12), fg="purple")
            summary_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            summary_scrollbar.config(command=summary_display.yview)
            summary_display.config(state=tk.NORMAL)
            
            # Make popup visible and update
            popup.update()
            
            # Get summary from copilot
            strategy_summary = []
            for chunk in copilot_stream(summary_prompt, app.workspace_path):
                if chunk:
                    strategy_summary.append(chunk)
                    summary_display.insert(tk.END, chunk + "\n")
                    summary_display.see(tk.END)
                    summary_display.update_idletasks()
                    popup.update()
            
            summary_display.config(state=tk.DISABLED)
            
            # Close the popup window
            popup.destroy()
            
            full_summary = "\n".join(strategy_summary).strip()
            
            # Create strategy file
            strategy_file = os.path.join(app.case_dir, f"strategy-{task_number}.md")
            os.makedirs(os.path.dirname(strategy_file), exist_ok=True)
            
            with open(strategy_file, 'w', encoding='utf-8') as f:
                f.write(full_summary)
            
            app.chat_display.config(state=tk.NORMAL)
            app.chat_display.insert(tk.END, f"Strategy summary saved to {strategy_file}\n", "copilot")
            app.chat_display.see(tk.END)
            app.chat_display.config(state=tk.DISABLED)
            
            # Check if a tab with this name already exists
            tab_label = f"V{task_number}"
            existing_tab = None
            for tab in app.strategies_notebook.tabs():
                if app.strategies_notebook.tab(tab, "text") == tab_label:
                    existing_tab = tab
                    break
            
            if existing_tab:
                # Overwrite existing tab by updating its content
                from file_loader import find_text_widget
                tab_frame = app.strategies_notebook.nametowidget(existing_tab)
                text_widget = find_text_widget(tab_frame)
                if text_widget:
                    from markdown_renderer import render_markdown
                    text_widget.config(state=tk.NORMAL)
                    text_widget.delete("1.0", tk.END)
                    with open(strategy_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    render_markdown(text_widget, content)
                    text_widget.config(state=tk.DISABLED)
                # Switch to the existing tab
                app.strategies_notebook.select(existing_tab)
            else:
                # Open the strategy file in a new tab in the Strategies pane
                from file_loader import load_single_file_as_tab
                load_single_file_as_tab(app, app.strategies_notebook, strategy_file, tab_label)
                # Switch to the newly created strategy tab
                last_tab = app.strategies_notebook.tabs()[-1]
                app.strategies_notebook.select(last_tab)
            
            # Update highest strategy version and button visibility
            from event_handlers import update_highest_version, handle_strategy_tab_changed
            app.highest_strategy_version = update_highest_version(app.strategies_notebook, 'highest_strategy_version')
            handle_strategy_tab_changed(app)
            
            app.chat_display.config(state=tk.NORMAL)
            app.chat_display.insert(tk.END, f"Strategy tab opened for V{task_number}\n\n", "copilot")
            app.chat_display.see(tk.END)
            app.chat_display.config(state=tk.DISABLED)
        else:
            app.chat_display.config(state=tk.NORMAL)
            app.chat_display.insert(tk.END, "Warning: Could not find automate() function in generated code\n\n", "copilot")
            app.chat_display.see(tk.END)
            app.chat_display.config(state=tk.DISABLED)


def execute_strategy(app):
    """Handle Execute button click
    
    Args:
        app: The ChatApp instance
    """
    # Get the current strategy tab
    current_tab = app.strategies_notebook.select()
    if not current_tab:
        return
    
    # Get the tab text (e.g., "V0001")
    tab_text = app.strategies_notebook.tab(current_tab, "text")
    
    # Extract the task number
    match = re.search(r'V(\d+)', tab_text)
    if match:
        task_number = match.group(1)
        
        # Construct the class name (same as in generate_strategy)
        task_name_clean = app.task_name.replace("-", "_")
        java_class_name = f"Code_{task_name_clean}_{task_number}"
        
        # Display message in chat window
        app.chat_display.config(state=tk.NORMAL)
        app.chat_display.insert(tk.END, f"Executing {java_class_name}...\n", "copilot")
        app.chat_display.see(tk.END)
        app.chat_display.config(state=tk.DISABLED)
        app.root.update_idletasks()
        
        # Run the Maven command
        maven_command = f'mvn compile exec:java "-Dexec.mainClass={java_class_name}" "-Dexec.classpathScope=compile"'
        
        app.chat_display.config(state=tk.NORMAL)
        app.chat_display.insert(tk.END, f"Running command: {maven_command}\n\n", "copilot")
        app.chat_display.see(tk.END)
        app.chat_display.config(state=tk.DISABLED)
        app.root.update_idletasks()
        
        # Execute in terminal and wait for completion
        import subprocess
        subprocess.run(maven_command, shell=True, cwd=app.workspace_path)
        
        # Task refinement after execution
        app.chat_display.config(state=tk.NORMAL)
        app.chat_display.insert(tk.END, "Generating refined task description...\n", "copilot")
        app.chat_display.see(tk.END)
        app.chat_display.config(state=tk.DISABLED)
        app.root.update_idletasks()
        
        # Read the prompt template and replace placeholders
        template_path = os.path.join(os.path.dirname(__file__), "prompt_refine_description_template.txt")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            refine_prompt = f.read().replace("{task_name}", app.task_name)

        # Create popup window for displaying refined task description
        popup = tk.Toplevel(app.root)
        popup.title("Task Refinement Output")
        popup.geometry("800x600")
        
        # Create text widget with scrollbar for task display
        task_frame = tk.Frame(popup)
        task_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        task_scrollbar = tk.Scrollbar(task_frame)
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        task_display = tk.Text(task_frame, wrap=tk.WORD, yscrollcommand=task_scrollbar.set, font=("Courier", 12), fg="blue")
        task_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scrollbar.config(command=task_display.yview)
        task_display.config(state=tk.NORMAL)
        
        # Make popup visible and update
        popup.update()
        
        # Stream copilot response and collect the refined task description
        refined_task = []
        for chunk in copilot_stream(refine_prompt, app.workspace_path):
            if chunk:
                refined_task.append(chunk)
                task_display.insert(tk.END, chunk + "\n")
                task_display.see(tk.END)
                task_display.update_idletasks()
                popup.update()
        
        task_display.config(state=tk.DISABLED)

        # Close the popup window
        popup.destroy()

        # Calculate next task number
        next_task_number = str(int(task_number) + 1).zfill(4)
        
        # Create the next version task file
        task_file = os.path.join(app.case_dir, f"task-{next_task_number}.md")
        os.makedirs(os.path.dirname(task_file), exist_ok=True)
        
        # Write the refined task description to file
        full_task = "\n".join(refined_task).strip()
        
        # Extract content between markdown code fences if present
        start_marker_match = re.search(r'^\s*```(?:markdown|md|[a-z]*)\s*$', full_task, re.MULTILINE)
        if start_marker_match:
            start_pos = start_marker_match.end()
            # Skip any whitespace/newline after the opening marker
            while start_pos < len(full_task) and full_task[start_pos] in '\r\n':
                start_pos += 1
            
            # Find the closing ``` after the start marker
            end_marker_match = re.search(r'^\s*```\s*$', full_task[start_pos:], re.MULTILINE)
            if end_marker_match:
                # Extract content between markers
                full_task = full_task[start_pos:start_pos + end_marker_match.start()]
        
        full_task = full_task.strip()
        
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(full_task)
        
        app.chat_display.config(state=tk.NORMAL)
        app.chat_display.insert(tk.END, f"Refined task saved to {task_file}\n", "copilot")
        app.chat_display.see(tk.END)
        app.chat_display.config(state=tk.DISABLED)
        
        # Check if a tab with this name already exists
        tab_label = f"V{next_task_number}"
        existing_tab = None
        for tab in app.tasks_notebook.tabs():
            if app.tasks_notebook.tab(tab, "text") == tab_label:
                existing_tab = tab
                break
        
        if existing_tab:
            # Overwrite existing tab by updating its content
            from file_loader import find_text_widget
            tab_frame = app.tasks_notebook.nametowidget(existing_tab)
            text_widget = find_text_widget(tab_frame)
            if text_widget:
                text_widget.delete("1.0", tk.END)
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_widget.insert(tk.END, content)
            # Switch to the existing tab
            app.tasks_notebook.select(existing_tab)
        else:
            # Open the task file in a new tab in the Tasks pane
            from file_loader import load_single_file_as_tab
            load_single_file_as_tab(app, app.tasks_notebook, task_file, tab_label)
            # Switch to the newly created task tab
            last_tab = app.tasks_notebook.tabs()[-1]
            app.tasks_notebook.select(last_tab)
        
        # Update highest task version
        from event_handlers import update_highest_version, handle_task_tab_changed
        app.highest_task_version = update_highest_version(app.tasks_notebook, 'highest_task_version')
        
        # Update button visibility for the new tab
        handle_task_tab_changed(app)
        
        app.chat_display.config(state=tk.NORMAL)
        app.chat_display.insert(tk.END, f"Task tab opened for V{next_task_number}\n\n", "copilot")
        app.chat_display.see(tk.END)
        app.chat_display.config(state=tk.DISABLED)
