"""UI components creation for the chat application"""
import tkinter as tk
from tkinter import ttk, scrolledtext


def create_main_panes(root):
    """Create main 60/40 split panes
    
    Args:
        root: The root window
        
    Returns:
        Tuple of (main_paned, left_paned)
    """
    # Create the main horizontal pane (60/40 split)
    main_paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    main_paned.pack(fill=tk.BOTH, expand=True)
    
    # Create the left vertical pane (for Tasks and Strategies)
    left_paned = tk.PanedWindow(main_paned, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=5)
    main_paned.add(left_paned, minsize=400)
    
    return main_paned, left_paned


def create_tasks_pane(parent):
    """Create Tasks pane with notebook and buttons
    
    Args:
        parent: The parent paned window
        
    Returns:
        Tuple of (tasks_frame, tasks_notebook, generate_strategy_button)
    """
    # Tasks pane (upper left)
    tasks_frame = tk.Frame(parent)
    parent.add(tasks_frame, minsize=200)
    
    # Top bar with "Tasks" label and buttons
    tasks_top_bar = tk.Frame(tasks_frame)
    tasks_top_bar.pack(fill=tk.X, padx=5, pady=5)
    
    # Label on left
    tasks_label = tk.Label(tasks_top_bar, text="Tasks", font=("Arial", 12, "bold"))
    tasks_label.pack(side='left')
    
    # Button container on right
    tasks_button_container = tk.Frame(tasks_top_bar)
    tasks_button_container.pack(side='right')
    
    # Generate Strategy button (shown for highest version)
    generate_strategy_button = tk.Button(tasks_button_container, text="Generate Strategy")
    
    # Create notebook for tasks
    tasks_notebook = ttk.Notebook(tasks_frame)
    tasks_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    return tasks_frame, tasks_notebook, generate_strategy_button


def create_strategies_pane(parent):
    """Create Strategies pane with notebook and Execute button
    
    Args:
        parent: The parent paned window
        
    Returns:
        Tuple of (strategies_frame, strategies_notebook, execute_button)
    """
    # Strategies pane (lower left)
    strategies_frame = tk.Frame(parent)
    parent.add(strategies_frame, minsize=200)
    
    # Top bar with "Strategies" label and Execute button
    strategies_top_bar = tk.Frame(strategies_frame)
    strategies_top_bar.pack(fill=tk.X, padx=5, pady=5)
    
    # Label on left
    strategies_label = tk.Label(strategies_top_bar, text="Strategies", font=("Arial", 12, "bold"))
    strategies_label.pack(side='left')
    
    # Button container on right
    strategies_button_container = tk.Frame(strategies_top_bar)
    strategies_button_container.pack(side='right')
    
    # Execute button (shown for highest version)
    execute_button = tk.Button(strategies_button_container, text="Execute", bg='red', fg='white')
    
    # Create notebook for strategies
    strategies_notebook = ttk.Notebook(strategies_frame)
    strategies_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    return strategies_frame, strategies_notebook, execute_button


def create_chat_pane(parent):
    """Create chat pane with output and input areas
    
    Args:
        parent: The parent paned window
        
    Returns:
        Tuple of (chat_frame, chat_output, chat_input, submit_button, open_task_button)
    """
    # Chat pane (right side)
    chat_frame = tk.Frame(parent)
    parent.add(chat_frame, minsize=400)
    
    # Top bar with "Chat" label and Open Task button
    chat_top_bar = tk.Frame(chat_frame)
    chat_top_bar.pack(fill=tk.X, padx=5, pady=5)
    
    # Chat label
    chat_label = tk.Label(chat_top_bar, text="Chat", font=("Arial", 12, "bold"))
    chat_label.pack(side='left')
    
    # Open Task button on right
    open_task_button = tk.Button(chat_top_bar, text="Open Task")
    open_task_button.pack(side='right')
    
    # Chat output area
    chat_output = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state='disabled', height=20)
    chat_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    # Configure text tags for colored output
    chat_output.tag_config('user', foreground='green')
    chat_output.tag_config('copilot', foreground='blue')
    chat_output.tag_config('error', foreground='red')
    
    # Input area
    input_frame = tk.Frame(chat_frame)
    input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
    
    chat_input = tk.Entry(input_frame)
    chat_input.pack(side='left', fill=tk.BOTH, expand=True, padx=(0, 5))
    
    submit_button = tk.Button(input_frame, text="Submit")
    submit_button.pack(side='right')
    
    return chat_frame, chat_output, chat_input, submit_button, open_task_button


def configure_notebook_styles():
    """Configure TTK styles for notebooks
    
    Returns:
        The configured ttk.Style object
    """
    style = ttk.Style()
    
    # Configure the active tab style with green background and white text
    style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10))
    style.map('TNotebook.Tab',
              background=[('selected', 'green')],
              foreground=[('selected', 'white')],
              font=[('selected', ('Arial', 10, 'bold'))])
    
    return style
