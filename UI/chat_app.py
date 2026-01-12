import tkinter as tk
from tkinter import scrolledtext, ttk
import os
import sys

# Add the UI directory to the path to import copilot module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from copilot import copilot_stream

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("1000x600")
        
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
        
        # Add "Tasks" label
        tasks_label = tk.Label(upper_left, text="Tasks", bg="white", font=("Arial", 12, "bold"))
        tasks_label.pack(pady=5)
        
        # Create notebook (tabbed interface) for task files
        self.tasks_notebook = ttk.Notebook(upper_left)
        self.tasks_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Load task files from tasks/2025-08-27 directory
        self.load_files_as_tabs(self.tasks_notebook, "task-*.md")
        
        # Lower-left pane (50% of left pane) - Strategies editor
        lower_left = tk.Frame(left_pane, bg="white", relief=tk.RIDGE, borderwidth=2)
        lower_left.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add "Strategies" label
        strategies_label = tk.Label(lower_left, text="Strategies", bg="white", font=("Arial", 12, "bold"))
        strategies_label.pack(pady=5)
        
        # Create notebook (tabbed interface) for strategy files
        self.strategies_notebook = ttk.Notebook(lower_left)
        self.strategies_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Load strategy files from tasks/2025-08-27 directory
        self.load_files_as_tabs(self.strategies_notebook, "strategy-*.md")
        
        main_container.add(left_pane, width=600)
        
        # Right pane (40% of window) - Chat window
        right_pane = tk.Frame(main_container, bg="white", relief=tk.RIDGE, borderwidth=2)
        main_container.add(right_pane, width=400)
        
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
        self.input_box.insert(0, "Please summarize file tasks\\2025-08-27\\task-0004.md using less than 200 words")
        
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
            for chunk in copilot_stream(message):
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
    
    def load_files_as_tabs(self, notebook, file_pattern):
        """Load filtered files from tasks/2025-08-27 directory as tabs
        
        Args:
            notebook: The notebook widget to add tabs to
            file_pattern: File pattern to match (e.g., 'task-*.md' or 'strategy-*.md')
        """
        import fnmatch
        
        # Get the tasks directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tasks_dir = os.path.join(base_dir, "tasks", "2025-08-27")
        
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
            
            # Create a scrolled text widget for the file content
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
                    text_widget.insert(tk.END, content)
            except Exception as e:
                text_widget.insert(tk.END, f"Error loading file: {e}")
            
            # Add the tab to the notebook with the V* label
            notebook.add(tab_frame, text=tab_label)

def main():
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
