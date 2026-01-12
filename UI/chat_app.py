import tkinter as tk
from tkinter import scrolledtext, ttk
import os
import sys
import re

# Add the UI directory to the path to import copilot module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from copilot import copilot_stream

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("2000x1200")
        
        # Set workspace path for copilot commands
        self.workspace_path = "D:\\repos\\MSR-Web-Verbs"
        self.task_name = "2025-08-27"
        self.case_dir = os.path.join(self.workspace_path, "tasks", self.task_name)
        
        # Configure notebook tab styles to make active tab more prominent
        style = ttk.Style()
        style.theme_use('default')
        
        # Style for selected (active) tab
        style.configure('TNotebook.Tab', 
                       padding=[10, 5], 
                       font=('Arial', 10))
        style.map('TNotebook.Tab',
                 background=[('selected', '#4CAF50'), ('!selected', '#E0E0E0')],
                 foreground=[('selected', 'white'), ('!selected', 'black')],
                 font=[('selected', ('Arial', 10, 'bold')), ('!selected', ('Arial', 10))])
        
        # Create main container with PanedWindow for 60/40 split
        main_container = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=5)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left pane (60% of window)
        left_pane = tk.Frame(main_container, bg="lightgray")
        
        # Configure grid weights for left pane
        left_pane.grid_rowconfigure(0, weight=1)
        left_pane.grid_rowconfigure(1, weight=1)
        left_pane.grid_columnconfigure(0, weight=1)
        
        # Upper-left pane (50% of left pane) - Tasks editor
        upper_left = tk.Frame(left_pane, bg="white", relief=tk.RIDGE, borderwidth=2)
        upper_left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Header frame for label and buttons
        tasks_header_frame = tk.Frame(upper_left, bg="white")
        tasks_header_frame.pack(fill=tk.X, pady=5)
        
        # Add "Tasks" label
        tasks_label = tk.Label(tasks_header_frame, text="Tasks", bg="white", font=("Arial", 12, "bold"))
        tasks_label.pack(side=tk.LEFT, padx=5)
        
        # Button frame for right-aligned buttons
        tasks_button_frame = tk.Frame(tasks_header_frame, bg="white")
        tasks_button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Generate Strategy button
        self.generate_strategy_button = tk.Button(
            tasks_button_frame,
            text="Generate Strategy",
            command=self.generate_strategy,
            bg="#FF9800",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10
        )
        self.generate_strategy_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete button
        self.delete_task_button = tk.Button(
            tasks_button_frame,
            text="Delete",
            command=self.delete_task,
            bg="#F44336",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10
        )
        self.delete_task_button.pack(side=tk.LEFT)
        
        # Initially hide the buttons
        self.generate_strategy_button.pack_forget()
        self.delete_task_button.pack_forget()
        
        # Create notebook (tabbed interface) for task files
        self.tasks_notebook = ttk.Notebook(upper_left)
        self.tasks_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event to update button visibility
        self.tasks_notebook.bind("<<NotebookTabChanged>>", self.on_task_tab_changed)
        
        # Load task files from tasks/2025-08-27 directory
        self.load_files_as_tabs(self.tasks_notebook, "task-*.md")
        
        # Store the highest task version for comparison
        self.update_highest_task_version()
        
        # Lower-left pane (50% of left pane) - Strategies editor
        lower_left = tk.Frame(left_pane, bg="white", relief=tk.RIDGE, borderwidth=2)
        lower_left.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Header frame for label and button
        strategies_header_frame = tk.Frame(lower_left, bg="white")
        strategies_header_frame.pack(fill=tk.X, pady=5)
        
        # Add "Strategies" label
        strategies_label = tk.Label(strategies_header_frame, text="Strategies", bg="white", font=("Arial", 12, "bold"))
        strategies_label.pack(side=tk.LEFT, padx=5)
        
        # Button frame for right-aligned button
        strategies_button_frame = tk.Frame(strategies_header_frame, bg="white")
        strategies_button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Execute button
        self.execute_button = tk.Button(
            strategies_button_frame,
            text="Execute",
            command=self.execute_strategy,
            bg="#F44336",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10
        )
        self.execute_button.pack(side=tk.LEFT)
        
        # Initially hide the button
        self.execute_button.pack_forget()
        
        # Create notebook (tabbed interface) for strategy files
        self.strategies_notebook = ttk.Notebook(lower_left)
        self.strategies_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event to update button visibility
        self.strategies_notebook.bind("<<NotebookTabChanged>>", self.on_strategy_tab_changed)
        
        # Load strategy files from tasks/2025-08-27 directory
        self.load_files_as_tabs(self.strategies_notebook, "strategy-*.md")
        
        # Store the highest strategy version for comparison
        self.update_highest_strategy_version()
        
        main_container.add(left_pane, width=600)
        
        # Right pane (40% of window) - Chat window
        right_pane = tk.Frame(main_container, bg="white", relief=tk.RIDGE, borderwidth=2)
        main_container.add(right_pane, width=400)
        
        # Task name control frame at the top of right pane
        task_control_frame = tk.Frame(right_pane)
        task_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label for task name
        task_label = tk.Label(task_control_frame, text="Task Name:", font=("Arial", 10))
        task_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Input box for task name
        self.task_name_input = tk.Entry(task_control_frame, font=("Arial", 10))
        self.task_name_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.task_name_input.insert(0, self.task_name)
        
        # Open Task button
        open_task_button = tk.Button(
            task_control_frame,
            text="Open Task",
            command=self.open_task,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        open_task_button.pack(side=tk.RIGHT)
        
        # Chat display area (scrollable text widget)
        chat_frame = tk.Frame(right_pane)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=40,
            height=20,
            state=tk.DISABLED,
            bg="white",
            font=("Arial", 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.chat_display.tag_config("user", foreground="green")
        self.chat_display.tag_config("copilot", foreground="blue")
        self.chat_display.tag_config("error", foreground="red")
        
        # Input area at the bottom of right pane
        input_frame = tk.Frame(right_pane)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input text box
        self.input_box = tk.Entry(input_frame, font=("Arial", 10))
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Bind Enter key to submit
        self.input_box.bind("<Return>", lambda event: self.submit_message())
        
        # Submit button
        submit_button = tk.Button(
            input_frame,
            text="Submit",
            command=self.submit_message,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15
        )
        submit_button.pack(side=tk.RIGHT)
        
        # Set the 60/40 split after window updates
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        main_container.sash_place(0, int(window_width * 0.6), 0)
        
        # Pre-populate the input box with the prompt
        self.input_box.insert(0, "Please summarize task 0004 using less than 200 words")
        
    def submit_message(self):
        """Handle message submission"""
        message = self.input_box.get().strip()
        
        if message:
            # Enable chat display to insert user's prompt
            self.chat_display.config(state=tk.NORMAL)
            
            # Append user's prompt to chat display
            self.chat_display.insert(tk.END, f"User: {message}\n", "user")
            
            # Auto-scroll to the bottom
            self.chat_display.see(tk.END)
            
            # Disable chat display temporarily
            self.chat_display.config(state=tk.DISABLED)
            
            # Update the UI to show the message
            self.root.update_idletasks()
            
            # Enable chat display to insert response
            self.chat_display.config(state=tk.NORMAL)
            
            # Insert copilot label
            self.chat_display.insert(tk.END, "Copilot: ", "copilot")
            
            # Stream copilot responses as they arrive
            response_received = False
            for chunk in copilot_stream(message, self.case_dir):
                if chunk:
                    response_received = True
                    self.chat_display.insert(tk.END, "\n" + chunk, "copilot")
                    self.chat_display.see(tk.END)
                    self.root.update_idletasks()  # Force UI update for each chunk
            
            if not response_received:
                self.chat_display.insert(tk.END, "No response or error occurred.", "error")
            
            # Add spacing after response
            self.chat_display.insert(tk.END, "\n\n")
            
            # Auto-scroll to the bottom
            self.chat_display.see(tk.END)
            
            # Disable chat display to prevent manual editing
            self.chat_display.config(state=tk.DISABLED)
            
            # Clear the input box
            self.input_box.delete(0, tk.END)
            
            # Set focus back to input box
            self.input_box.focus_set()
    
    def open_task(self):
        """Handle opening a new task by reloading tabs with the new task name"""
        new_task_name = self.task_name_input.get().strip()
        
        if new_task_name and new_task_name != self.task_name:
            # Update task name
            self.task_name = new_task_name
            
            # Clear existing tabs
            for tab in self.tasks_notebook.tabs():
                self.tasks_notebook.forget(tab)
            for tab in self.strategies_notebook.tabs():
                self.strategies_notebook.forget(tab)
            
            # Reload tabs with new task name
            self.load_files_as_tabs(self.tasks_notebook, "task-*.md")
            self.load_files_as_tabs(self.strategies_notebook, "strategy-*.md")
            
            # Update highest task version and button visibility
            self.update_highest_task_version()
            self.update_highest_strategy_version()
            self.on_task_tab_changed()
            self.on_strategy_tab_changed()
    
    def update_highest_task_version(self):
        """Update the highest task version number"""
        self.highest_task_version = None
        tabs = self.tasks_notebook.tabs()
        
        if tabs:
            # Extract version numbers from tab labels
            import re
            versions = []
            for tab in tabs:
                tab_text = self.tasks_notebook.tab(tab, "text")
                match = re.search(r'V(\d+)', tab_text)
                if match:
                    versions.append(int(match.group(1)))
            
            if versions:
                self.highest_task_version = max(versions)
    
    def update_highest_strategy_version(self):
        """Update the highest strategy version number"""
        self.highest_strategy_version = None
        tabs = self.strategies_notebook.tabs()
        
        if tabs:
            # Extract version numbers from tab labels
            import re
            versions = []
            for tab in tabs:
                tab_text = self.strategies_notebook.tab(tab, "text")
                match = re.search(r'V(\d+)', tab_text)
                if match:
                    versions.append(int(match.group(1)))
            
            if versions:
                self.highest_strategy_version = max(versions)
    
    def on_task_tab_changed(self, event=None):
        """Handle task tab change to show/hide buttons"""
        if not hasattr(self, 'highest_task_version') or self.highest_task_version is None:
            return
        
        # Get current tab
        current_tab = self.tasks_notebook.select()
        if current_tab:
            tab_text = self.tasks_notebook.tab(current_tab, "text")
            
            # Check if this is the highest version
            import re
            match = re.search(r'V(\d+)', tab_text)
            if match and int(match.group(1)) == self.highest_task_version:
                # Show buttons
                self.generate_strategy_button.pack(side=tk.LEFT, padx=(0, 5))
                self.delete_task_button.pack(side=tk.LEFT)
            else:
                # Hide buttons
                self.generate_strategy_button.pack_forget()
                self.delete_task_button.pack_forget()
    
    def on_strategy_tab_changed(self, event=None):
        """Handle strategy tab change to show/hide Execute button"""
        if not hasattr(self, 'highest_strategy_version') or self.highest_strategy_version is None:
            return
        
        # Get current tab
        current_tab = self.strategies_notebook.select()
        if current_tab:
            tab_text = self.strategies_notebook.tab(current_tab, "text")
            
            # Check if this is the highest version
            import re
            match = re.search(r'V(\d+)', tab_text)
            if match and int(match.group(1)) == self.highest_strategy_version:
                # Show button
                self.execute_button.pack(side=tk.LEFT)
            else:
                # Hide button
                self.execute_button.pack_forget()
    
    def generate_strategy(self):
        """Handle Generate Strategy button click"""
        # TODO: Implement strategy generation logic
        print("Generate Strategy clicked for highest task version")
    
    def delete_task(self):
        """Handle Delete button click"""
        # TODO: Implement task deletion logic
        print("Delete clicked for highest task version")
    
    def execute_strategy(self):
        """Handle Execute button click"""
        # TODO: Implement strategy execution logic
        print("Execute clicked for highest strategy version")
    
    def load_files_as_tabs(self, notebook, file_pattern):
        """Load filtered files from tasks/2025-08-27 directory as tabs
        
        Args:
            notebook: The notebook widget to add tabs to
            file_pattern: File pattern to match (e.g., 'task-*.md' or 'strategy-*.md')
        """
        import fnmatch
        
        # Determine if this is for strategies (read-only renderer) or tasks (editable)
        is_strategy = file_pattern.startswith("strategy-")
        
        # Get the tasks directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tasks_dir = os.path.join(base_dir, "tasks", self.task_name)
        
        if not os.path.exists(tasks_dir):
            # If directory doesn't exist, show a message
            empty_frame = tk.Frame(notebook)
            label = tk.Label(empty_frame, text=f"Directory not found: {tasks_dir}")
            label.pack(pady=20)
            notebook.add(empty_frame, text="Error")
            return
        
        # Get all files in the directory that match the pattern
        all_files = [f for f in os.listdir(tasks_dir) if os.path.isfile(os.path.join(tasks_dir, f))]
        files = sorted([f for f in all_files if fnmatch.fnmatch(f, file_pattern)])
        
        if not files:
            # If no files, show a message
            empty_frame = tk.Frame(notebook)
            label = tk.Label(empty_frame, text=f"No files found matching {file_pattern}")
            label.pack(pady=20)
            notebook.add(empty_frame, text="Empty")
            return
        
        # Create a tab for each file
        for filename in files:
            file_path = os.path.join(tasks_dir, filename)
            
            # Extract number from filename and create tab label (e.g., "task-0001.md" -> "V0001")
            import re
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
                    font=("Consolas", 10),
                    bg="#f5f5f5",
                    state=tk.DISABLED
                )
                text_widget.pack(fill=tk.BOTH, expand=True)
                
                # Configure tags for markdown formatting
                text_widget.tag_configure("h1", font=("Arial", 16, "bold"), spacing3=10)
                text_widget.tag_configure("h2", font=("Arial", 14, "bold"), spacing3=8)
                text_widget.tag_configure("h3", font=("Arial", 12, "bold"), spacing3=6)
                text_widget.tag_configure("bold", font=("Consolas", 10, "bold"))
                text_widget.tag_configure("italic", font=("Consolas", 10, "italic"))
                text_widget.tag_configure("code", font=("Courier", 9), background="#e0e0e0")
                text_widget.tag_configure("code_block", font=("Courier", 9), background="#e0e0e0", lmargin1=20, lmargin2=20)
            else:
                # For tasks: create editable text widget
                text_widget = scrolledtext.ScrolledText(
                    tab_frame,
                    wrap=tk.WORD,
                    font=("Consolas", 10),
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
                        self.render_markdown(text_widget, content)
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
    
    def render_markdown(self, text_widget, content):
        """Render markdown content with basic formatting in a text widget"""
        lines = content.split('\n')
        in_code_block = False
        
        for line in lines:
            # Check for code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                text_widget.insert(tk.END, '\n')
                continue
            
            if in_code_block:
                text_widget.insert(tk.END, line + '\n', "code_block")
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
                self.render_inline_markdown(text_widget, line)
                text_widget.insert(tk.END, '\n')
    
    def render_inline_markdown(self, text_widget, line):
        """Render inline markdown formatting (bold, italic, code)"""
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

def main():
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
