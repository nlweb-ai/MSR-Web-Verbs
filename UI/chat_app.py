"""Main chat application for Browser Agent Based On Web Verbs"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import sys

# Add the UI directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_loader import load_files_as_tabs
from event_handlers import update_highest_version, handle_task_tab_changed, handle_strategy_tab_changed
from action_handlers import submit_message, open_task, generate_strategy, execute_strategy


class ChatApp:
    """Main application class for the chat interface"""
    
    def __init__(self, root):
        """Initialize the chat application
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("Browser Agent Based On Web Verbs")
        self.root.geometry("2000x1200")
        
        # Set workspace path for copilot commands
        self.workspace_path = "D:\\repos\\MSR-Web-Verbs"
        
        # Read task_name from cache.txt or use default
        cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache.txt")
        try:
            with open(cache_file, 'r') as f:
                self.task_name = f.read().strip()
                if not self.task_name:  # If cache is empty, use default
                    self.task_name = "2026-01-12"
        except FileNotFoundError:
            self.task_name = "2026-01-12"
        
        self.case_dir = os.path.join(self.workspace_path, "tasks", self.task_name)
        
        # Configure notebook tab styles
        self._configure_styles()
        
        # Create UI components
        self._create_ui()
        
        # Load initial data
        self._load_initial_data()
        
        # Set the 60/40 split after window updates
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        self.main_container.sash_place(0, int(window_width * 0.6), 0)
        
        # Pre-populate the input box with a sample prompt
        self.input_box.insert(0, "")
    
    def _configure_styles(self):
        """Configure TTK styles for the application"""
        style = ttk.Style()
        style.theme_use('default')
        
        # Style for notebook tabs
        style.configure('TNotebook.Tab', 
                       padding=[10, 5], 
                       font=('Arial', 12))
        style.map('TNotebook.Tab',
                 background=[('selected', '#4CAF50'), ('!selected', '#E0E0E0')],
                 foreground=[('selected', 'white'), ('!selected', 'black')],
                 font=[('selected', ('Arial', 12, 'bold')), ('!selected', ('Arial', 12))])
    
    def _create_ui(self):
        """Create all UI components"""
        # Create main container with PanedWindow for 60/40 split
        self.main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left pane with tasks and strategies
        self._create_left_pane()
        
        # Create right pane with chat
        self._create_right_pane()
    
    def _create_left_pane(self):
        """Create left pane with tasks and strategies notebooks"""
        # Left pane container
        left_pane = tk.Frame(self.main_container, bg="lightgray")
        
        # Configure grid weights for 50/50 split
        left_pane.grid_rowconfigure(0, weight=1)
        left_pane.grid_rowconfigure(1, weight=1)
        left_pane.grid_columnconfigure(0, weight=1)
        
        # Create tasks pane (upper left)
        self._create_tasks_pane(left_pane)
        
        # Create strategies pane (lower left)
        self._create_strategies_pane(left_pane)
        
        self.main_container.add(left_pane, width=600)
    
    def _create_tasks_pane(self, parent):
        """Create tasks pane with notebook and buttons"""
        # Upper-left pane - Tasks editor
        upper_left = tk.Frame(parent, bg="white", relief=tk.RIDGE, borderwidth=2)
        upper_left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Header frame for label and buttons
        tasks_header_frame = tk.Frame(upper_left, bg="white")
        tasks_header_frame.pack(fill=tk.X, pady=5)
        
        # Tasks label
        tasks_label = tk.Label(tasks_header_frame, text="Tasks", bg="white", font=("Arial", 14, "bold"))
        tasks_label.pack(side=tk.LEFT, padx=5)
        
        # Button frame for right-aligned buttons
        tasks_button_frame = tk.Frame(tasks_header_frame, bg="white")
        tasks_button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Generate Strategy button
        self.generate_strategy_button = tk.Button(
            tasks_button_frame,
            text="Generate Strategy",
            command=lambda: generate_strategy(self),
            bg="#FF9800",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10
        )
        
        # Create notebook for tasks
        self.tasks_notebook = ttk.Notebook(upper_left)
        self.tasks_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event
        self.tasks_notebook.bind("<<NotebookTabChanged>>", lambda e: handle_task_tab_changed(self, e))
    
    def _create_strategies_pane(self, parent):
        """Create strategies pane with notebook and Execute button"""
        # Lower-left pane - Strategies viewer
        lower_left = tk.Frame(parent, bg="white", relief=tk.RIDGE, borderwidth=2)
        lower_left.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Header frame for label and button
        strategies_header_frame = tk.Frame(lower_left, bg="white")
        strategies_header_frame.pack(fill=tk.X, pady=5)
        
        # Strategies label
        strategies_label = tk.Label(strategies_header_frame, text="Strategies", bg="white", font=("Arial", 14, "bold"))
        strategies_label.pack(side=tk.LEFT, padx=5)
        
        # Button frame for right-aligned button
        strategies_button_frame = tk.Frame(strategies_header_frame, bg="white")
        strategies_button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Execute button
        self.execute_button = tk.Button(
            strategies_button_frame,
            text="Execute",
            command=lambda: execute_strategy(self),
            bg="#F44336",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10
        )
        
        # Create notebook for strategies
        self.strategies_notebook = ttk.Notebook(lower_left)
        self.strategies_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event
        self.strategies_notebook.bind("<<NotebookTabChanged>>", lambda e: handle_strategy_tab_changed(self, e))
    
    def _create_right_pane(self):
        """Create right pane with chat interface"""
        # Right pane - Chat window
        right_pane = tk.Frame(self.main_container, bg="white", relief=tk.RIDGE, borderwidth=2)
        self.main_container.add(right_pane, width=400)
        
        # Task name control frame at the top
        task_control_frame = tk.Frame(right_pane)
        task_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Task name label
        task_label = tk.Label(task_control_frame, text="Task Name:", font=("Arial", 12))
        task_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Task name input
        self.task_name_input = tk.Entry(task_control_frame, font=("Arial", 12))
        self.task_name_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.task_name_input.insert(0, self.task_name)
        
        # Open Task button
        open_task_button = tk.Button(
            task_control_frame,
            text="Open Task",
            command=lambda: open_task(self),
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10
        )
        open_task_button.pack(side=tk.RIGHT)
        
        # Chat display area
        chat_frame = tk.Frame(right_pane)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=40,
            height=20,
            state=tk.DISABLED,
            bg="white",
            font=("Arial", 12)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.chat_display.tag_config("user", foreground="green")
        self.chat_display.tag_config("copilot", foreground="blue")
        self.chat_display.tag_config("error", foreground="red")
        
        # Input area at the bottom
        input_frame = tk.Frame(right_pane)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input text box
        self.input_box = tk.Entry(input_frame, font=("Arial", 12))
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Bind Enter key to submit
        self.input_box.bind("<Return>", lambda event: submit_message(self))
        
        # New button
        new_button = tk.Button(
            input_frame,
            text="New",
            command=lambda: self._clear_chat(),
            bg="#FF9800",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=15
        )
        new_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Submit button
        submit_button = tk.Button(
            input_frame,
            text="Submit",
            command=lambda: submit_message(self),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=15
        )
        submit_button.pack(side=tk.RIGHT)
    
    def _load_initial_data(self):
        """Load initial task and strategy files"""
        # Load task files
        load_files_as_tabs(self, self.tasks_notebook, "task-*.md")
        
        # Store the highest task version
        self.highest_task_version = update_highest_version(self.tasks_notebook, 'highest_task_version')
        
        # Load strategy files
        load_files_as_tabs(self, self.strategies_notebook, "strategy-*.md")
        
        # Store the highest strategy version
        self.highest_strategy_version = update_highest_version(self.strategies_notebook, 'highest_strategy_version')
        
        # Trigger initial button visibility updates
        handle_task_tab_changed(self)
        handle_strategy_tab_changed(self)
    
    def _clear_chat(self):
        """Clear the chat display window"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
