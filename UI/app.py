"""Main chat application for Browser Agent Based On Web Verbs"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
import queue
import sys
import ctypes
import ctypes.wintypes
import threading
import time
import subprocess
import shutil

# Add the UI directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Add verbs directory for cdp_utils
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "verbs"))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import debug_state, _step_event, _lock

from file_loader import load_files_as_tabs
from event_handlers import update_highest_version, handle_task_tab_changed, handle_strategy_tab_changed
from action_handlers import submit_message, open_task, create_task, generate_strategy, execute_strategy, save_task, preview_task, modify_task


def _add_tooltip(widget, text):
    """Show a tooltip on hover for the given widget."""
    tip = None

    def on_enter(event):
        nonlocal tip
        tip = tk.Toplevel(widget)
        tip.wm_overrideredirect(True)
        x = widget.winfo_rootx() + widget.winfo_width() // 2
        y = widget.winfo_rooty() + widget.winfo_height() + 4
        tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tip, text=text, bg="#333", fg="white", font=("Arial", 10),
                         padx=6, pady=2, relief=tk.SOLID, borderwidth=1)
        label.pack()

    def on_leave(event):
        nonlocal tip
        if tip:
            tip.destroy()
            tip = None

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


class ChatApp:
    """Main application class for the chat interface"""
    
    def __init__(self, root):
        """Initialize the chat application
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("Browser Agent Based On Web Verbs")
        
        # Set workspace path for copilot commands
        self.workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
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

        # Shared Chrome browser state
        self.chrome_ws_url = None
        self.chrome_proc = None
        self.chrome_profile_dir = None
        self._chrome_hwnd = None
        self._chrome_debug_port = None
        # Playwright worker thread state.
        # All page calls MUST run on the same thread that called sync_playwright().start().
        # We keep one persistent worker thread alive and submit tasks via _pw_task_queue.
        self._pw_task_queue = queue.SimpleQueue()   # items: (callable(page) -> result, result_queue) | None
        self._pw_worker_thread = None
        self.page = None         # set by worker thread once Chrome is ready
        self._work = (0, 0, 0, 0)
        self._debugger_win = None  # Toplevel debugger window
        self._dbg_widgets = {}     # debugger UI widgets

        # Configure notebook tab styles
        self._configure_styles()
        
        # Create UI components
        self._create_ui()
        
        # Load initial data
        self._load_initial_data()
        
        # Get usable working area (excluding taskbar)
        SPI_GETWORKAREA = 48
        work_rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(work_rect), 0)
        work_x = work_rect.left
        work_y = work_rect.top
        work_w = work_rect.right - work_rect.left
        work_h = work_rect.bottom - work_rect.top

        self._work = (work_x, work_y, work_w, work_h)

        # Position Tkinter window on the left half of the working area.
        # First pass: place the window so we can measure the title bar height.
        self.root.geometry(f"{work_w // 2}x{work_h}+{work_x}+{work_y}")
        self.root.update_idletasks()
        # Tkinter geometry height = content area only (title bar is extra).
        # Shrink by the title bar height so the outer frame fits exactly in work_h.
        title_bar_h = self.root.winfo_rooty() - work_y
        tkinter_h = work_h - title_bar_h
        self.root.geometry(f"{work_w // 2}x{tkinter_h}+{work_x}+{work_y}")
        self.root.update_idletasks()

        # Split three panes equally: Chat, Tasks, Strategies each get 1/3
        self.left_pane.sash_place(0, 0, tkinter_h // 3)
        self.left_pane.sash_place(1, 0, (tkinter_h * 2) // 3)

        # Pre-populate the input box with a sample prompt
        self.input_box.insert(0, "")

        # Launch shared Chrome on the right half and register close handler
        self._launch_shared_chrome(work_x, work_y, work_w, work_h, title_bar_h)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
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
        
        # Style for Strategies notebook tabs
        style.configure('Strategies.TNotebook.Tab',
                       padding=[10, 5],
                       font=('Arial', 12))
        style.map('Strategies.TNotebook.Tab',
                 background=[('selected', '#F57C00'), ('!selected', '#E0E0E0')],
                 foreground=[('selected', 'white'), ('!selected', 'black')],
                 font=[('selected', ('Arial', 12, 'bold')), ('!selected', ('Arial', 12))])
    
    def _create_ui(self):
        """Create all UI components"""
        # Control panel pinned at the very top
        self._create_control_panel()

        # Single vertical PanedWindow fills the rest of the Tkinter window (left half of screen)
        self.left_pane = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=5)
        self.left_pane.pack(fill=tk.BOTH, expand=True)

        # Three vertically stacked panes: Chat (upper), Tasks (middle), Strategies (lower)
        self._create_chat_pane(self.left_pane)
        self._create_tasks_pane(self.left_pane)
        self._create_strategies_pane(self.left_pane)
    
    def _create_control_panel(self):
        """Create the control panel bar at the top of the application."""
        panel = tk.Frame(self.root, bg="#ECECEC", relief=tk.GROOVE, borderwidth=1)
        panel.pack(fill=tk.X, side=tk.TOP)

        # --- Utility group (right) ---
        right_frame = tk.Frame(panel, bg="#ECECEC")
        right_frame.pack(side=tk.RIGHT, padx=8, pady=4)

        # Chrome connection status — click when failed to reconnect
        self._chrome_status_label = tk.Label(
            right_frame,
            text="Chrome: \u23f3 Connecting...",
            bg="#ECECEC", fg="#888", font=("Arial", 10),
            cursor="hand2"
        )
        self._chrome_status_label.pack(side=tk.RIGHT, padx=(0, 12))
        self._chrome_status_label.bind("<Button-1>", lambda _e: self._reconnect_chrome())

    def _create_tasks_pane(self, parent):
        """Create tasks pane with notebook and buttons"""
        # Upper-left pane - Tasks editor
        upper_left = tk.Frame(parent, bg="white", relief=tk.RIDGE, borderwidth=2)
        parent.add(upper_left)
        
        # Colored header bar
        tasks_header_frame = tk.Frame(upper_left, bg="#2E7D32")
        tasks_header_frame.pack(fill=tk.X)
        
        # Tasks label
        tasks_label = tk.Label(tasks_header_frame, text="Tasks", bg="#2E7D32", fg="white",
                               font=("Arial", 13, "bold"))
        tasks_label.pack(side=tk.LEFT, padx=8, pady=4)
        
        # Button frame for right-aligned buttons
        tasks_button_frame = tk.Frame(tasks_header_frame, bg="#2E7D32")
        tasks_button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Preview button (always visible)
        preview_task_button = tk.Button(
            tasks_button_frame,
            text="\U0001F441",
            command=lambda: preview_task(self),
            bg="#43A047",
            fg="white",
            font=("Arial", 14),
            padx=4, pady=2,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        preview_task_button.pack(side=tk.LEFT, padx=(0, 4))
        _add_tooltip(preview_task_button, "Render Markdown")

        # Save button (floppy disk icon, only visible on latest tab)
        self.save_task_button = tk.Button(
            tasks_button_frame,
            text="\U0001F4BE",
            command=lambda: save_task(self),
            bg="#43A047",
            fg="white",
            font=("Arial", 14),
            padx=4, pady=2,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        _add_tooltip(self.save_task_button, "Save")

        # Generate Strategy button (puzzle piece icon)
        self.generate_strategy_button = tk.Button(
            tasks_button_frame,
            text="\U0001F9E9",
            command=lambda: generate_strategy(self),
            bg="#E65100",
            fg="white",
            font=("Arial", 16),
            padx=4, pady=2,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        _add_tooltip(self.generate_strategy_button, "Generate Strategy")
        
        # Create notebook for tasks
        self.tasks_notebook = ttk.Notebook(upper_left)
        self.tasks_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event
        self.tasks_notebook.bind("<<NotebookTabChanged>>", lambda e: handle_task_tab_changed(self, e))
    
    def _create_strategies_pane(self, parent):
        """Create strategies pane with notebook and Execute button"""
        # Lower-left pane - Strategies viewer
        lower_left = tk.Frame(parent, bg="white", relief=tk.RIDGE, borderwidth=2)
        parent.add(lower_left)
        
        # Colored header bar
        strategies_header_frame = tk.Frame(lower_left, bg="#E65100")
        strategies_header_frame.pack(fill=tk.X)
        
        # Strategies label
        strategies_label = tk.Label(strategies_header_frame, text="Strategies", bg="#E65100", fg="white",
                                    font=("Arial", 13, "bold"))
        strategies_label.pack(side=tk.LEFT, padx=8, pady=4)
        
        # Button frame for right-aligned button
        strategies_button_frame = tk.Frame(strategies_header_frame, bg="#E65100")
        strategies_button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Execute button (play icon)
        self.execute_button = tk.Button(
            strategies_button_frame,
            text="\u25b6",
            command=lambda: execute_strategy(self),
            bg="#2E7D32",
            fg="white",
            font=("Arial", 16),
            padx=4, pady=2,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        _add_tooltip(self.execute_button, "Execute")
        
        # Create notebook for strategies
        self.strategies_notebook = ttk.Notebook(lower_left, style='Strategies.TNotebook')
        self.strategies_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event
        self.strategies_notebook.bind("<<NotebookTabChanged>>", lambda e: handle_strategy_tab_changed(self, e))
    
    def _create_chat_pane(self, parent):
        """Create chat pane (lower pane) with chat interface"""
        # Chat pane frame
        chat_pane = tk.Frame(parent, bg="white", relief=tk.RIDGE, borderwidth=2)
        parent.add(chat_pane)

        # Colored header bar
        chat_header = tk.Frame(chat_pane, bg="#1565C0")
        chat_header.pack(fill=tk.X)
        tk.Label(chat_header, text="Chat", bg="#1565C0", fg="white",
                 font=("Arial", 13, "bold")).pack(side=tk.LEFT, padx=8, pady=4)

        # Task name control frame at the top
        task_control_frame = tk.Frame(chat_pane)
        task_control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Task name label
        task_label = tk.Label(task_control_frame, text="Task Name:", font=("Arial", 12))
        task_label.pack(side=tk.LEFT, padx=(0, 5))

        # Task name dropdown (populated from tasks/ subfolders)
        tasks_root = os.path.join(self.workspace_path, "tasks")
        task_folders = sorted(
            [d for d in os.listdir(tasks_root)
             if os.path.isdir(os.path.join(tasks_root, d)) and d != "sample"],
            reverse=True
        )
        self.task_name_input = ttk.Combobox(
            task_control_frame, values=task_folders, font=("Arial", 12), state="readonly"
        )
        self.task_name_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        if self.task_name in task_folders:
            self.task_name_input.current(task_folders.index(self.task_name))
        elif task_folders:
            self.task_name_input.current(0)
        self.task_name_input.bind("<<ComboboxSelected>>", lambda e: open_task(self))

        # Reposition UI button
        reposition_btn = tk.Button(
            task_control_frame,
            text="\u267B",
            command=lambda: self.reposition_ui(),
            bg="#AB47BC",
            fg="white",
            font=("Arial", 14),
            padx=4, pady=2,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        reposition_btn.pack(side=tk.RIGHT)
        _add_tooltip(reposition_btn, "Reposition UI")

        # Create Task button
        create_task_btn = tk.Button(
            task_control_frame,
            text="\u2728",
            command=lambda: create_task(self),
            bg="#AB47BC",
            fg="white",
            font=("Arial", 14),
            padx=4, pady=2,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        create_task_btn.pack(side=tk.RIGHT)
        _add_tooltip(create_task_btn, "Create Task")

        # Chat display area
        chat_frame = tk.Frame(chat_pane)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=40,
            height=5,
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
        input_frame = tk.Frame(chat_pane)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input text box
        self.input_box = tk.Entry(input_frame, font=("Arial", 12))
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Bind Enter key to submit
        self.input_box.bind("<Return>", lambda event: submit_message(self))
        
        # New button
        new_button = tk.Button(
            input_frame,
            text="\u2795",
            command=lambda: self._clear_chat(),
            bg="#42A5F5",
            fg="white",
            font=("Arial", 14),
            padx=4, pady=2,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        new_button.pack(side=tk.RIGHT)
        _add_tooltip(new_button, "New Chat")
        
        # Modify Task button
        modify_task_button = tk.Button(
            input_frame,
            text="\U0001F4DD",
            command=lambda: modify_task(self),
            bg="#66BB6A",
            fg="white",
            font=("Arial", 14),
            padx=4, pady=2,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        modify_task_button.pack(side=tk.RIGHT)
        _add_tooltip(modify_task_button, "Modify Task")
        
        # Submit button
        submit_button = tk.Button(
            input_frame,
            text="\U0001F4AC",
            command=lambda: submit_message(self),
            bg="#42A5F5",
            fg="white",
            font=("Arial", 14),
            padx=4, pady=2,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        submit_button.pack(side=tk.RIGHT)
        _add_tooltip(submit_button, "Ask")
    
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

    # ------------------------------------------------------------------
    # Debug control stubs — wire these up to execution logic as needed
    # ------------------------------------------------------------------

    def _kill_all_chrome(self):
        """Kill all running Chrome processes and wait until they are fully gone."""
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "chrome.exe"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
        # Poll until tasklist confirms no chrome.exe remains (up to 8 seconds)
        deadline = time.time() + 8.0
        while time.time() < deadline:
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/NH"],
                    capture_output=True, text=True
                )
                if "chrome.exe" not in result.stdout:
                    break
            except Exception:
                break
            time.sleep(0.5)
        # Extra buffer to allow profile lock files to be released
        time.sleep(1.5)

    def _reset_chrome_crash_flag(self, user_data_dir: str):
        """Clear Chrome's crash-recovery flags and stale lock files so it starts
        cleanly without the 'restore pages?' dialog or singleton-lock conflicts."""
        # Remove stale lock files left by taskkill /F
        for lock_rel in [
            "lockfile",                              # User Data\lockfile
            os.path.join("Default", "lockfile"),     # User Data\Default\lockfile (some builds)
            os.path.join("Default", "SingletonLock"),# prevents Chrome from launching
        ]:
            lock_path = os.path.join(user_data_dir, lock_rel)
            try:
                if os.path.exists(lock_path):
                    os.remove(lock_path)
            except Exception:
                pass

        # Patch JSON preference files to suppress the crash-recovery dialog
        for rel_path, key in [
            (os.path.join("Default", "Preferences"), "profile"),
            (os.path.join("Local State"), None),
        ]:
            path = os.path.join(user_data_dir, rel_path)
            try:
                if not os.path.isfile(path):
                    continue
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if key:
                    data.setdefault(key, {})["exit_type"] = "Normal"
                    data.setdefault(key, {})["exited_cleanly"] = True
                else:
                    data.setdefault("stability", {})["exited_cleanly"] = True
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
            except Exception:
                pass

    def _launch_shared_chrome(self, work_x: int, work_y: int, work_w: int, work_h: int, title_bar_h: int = 0):
        """Launch Chrome via a persistent Playwright worker thread.

        Playwright's sync API is NOT thread-safe: all page calls must run on the
        same thread that called sync_playwright().start().  We keep one long-lived
        worker thread that (a) owns Chrome and (b) processes every automate() call
        submitted via self._pw_task_queue.
        """
        chrome_x = work_x + work_w // 2
        chrome_w = work_w - work_w // 2
        dbg_h = 90  # height reserved for the debugger bar above Chrome

        # Stop the previous worker thread before starting a new one
        if self._pw_worker_thread is not None and self._pw_worker_thread.is_alive():
            self._pw_task_queue.put(None)   # sentinel → worker exits
            self._pw_worker_thread.join(timeout=10)
        self._pw_task_queue = queue.SimpleQueue()
        self.page = None

        scale = 0.85
        chrome_x_dip = int(chrome_x / scale)
        chrome_y_dip = int((work_y + dbg_h) / scale)
        chrome_w_dip = int(chrome_w / scale)
        chrome_h_dip = int((work_h - dbg_h) / scale)

        # Dedicated Playwright profile — separate from Chrome's real default profile
        # (which Chrome forbids from CDP use).
        # On first run we copy the real profile's login files here so the user
        # doesn't have to log in again.  After that, this profile maintains its
        # own state (logins made inside the Playwright browser persist normally).
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        real_default   = os.path.join(local_app_data, "Google", "Chrome", "User Data", "Default")
        pw_profile      = os.path.join(local_app_data, "Google", "Chrome", "Playwright User Data")
        pw_default      = os.path.join(pw_profile, "Default")

        self.root.after(0, lambda: self._chrome_status_label.config(
            text="Chrome: \u23f3 Launching...", fg="#888"))

        def _pw_worker():
            """Owns the Playwright instance for its full lifetime."""
            self._kill_all_chrome()

            # First-time setup: copy login data from the real profile so the user
            # doesn't have to log in again.  We copy AFTER killing Chrome so SQLite
            # files are not open.  Existing pw_default is left untouched (preserves
            # logins the user did in a previous Playwright session).
            if not os.path.isdir(pw_default):
                os.makedirs(pw_default, exist_ok=True)
                real_user_data = os.path.dirname(real_default)  # …\Google\Chrome\User Data

                # MUST copy Local State — it contains os_crypt.encrypted_key which is
                # the DPAPI-wrapped AES key used to decrypt all cookies and passwords.
                # Without it the copied Cookies file is unreadable and Chrome logs out.
                for fname in ["Local State"]:
                    src = os.path.join(real_user_data, fname)
                    dst = os.path.join(pw_profile, fname)
                    try:
                        if os.path.exists(src):
                            shutil.copy2(src, dst)
                    except Exception:
                        pass

                # Per-profile data files
                for fname in [
                    "Cookies", "Cookies-journal",
                    "Login Data", "Login Data For Account",
                    "Web Data",
                ]:
                    src = os.path.join(real_default, fname)
                    dst = os.path.join(pw_default, fname)
                    try:
                        if os.path.exists(src):
                            shutil.copy2(src, dst)
                    except Exception:
                        pass

            self._reset_chrome_crash_flag(pw_profile)

            try:
                from playwright.sync_api import sync_playwright
                pw = sync_playwright().start()
                context = pw.chromium.launch_persistent_context(
                    pw_profile,
                    channel="chrome",
                    headless=False,
                    no_viewport=True,
                    args=[
                        f"--force-device-scale-factor={scale}",
                        f"--window-position={chrome_x_dip},{chrome_y_dip}",
                        f"--window-size={chrome_w_dip},{chrome_h_dip}",
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-infobars",
                    ]
                )
                # Always create a new page — it becomes the foreground tab in Chrome.
                # Any session-restored tabs remain in the background (harmless).
                self.page = context.new_page()
                self.root.after(0, lambda: self._chrome_status_label.config(
                    text="Chrome: \u2705 Connected", fg="#060"))
                self.root.after(0, lambda: self._show_debugger_window(chrome_x, work_y, chrome_w))
            except Exception as exc:
                err_msg = str(exc)
                def _show_err():
                    self._chrome_status_label.config(
                        text="Chrome: \u274c Failed (click to retry)", fg="#c00")
                    self.chat_display.config(state=tk.NORMAL)
                    self.chat_display.insert(
                        tk.END, f"\u26a0\ufe0f Chrome launch failed: {err_msg}\n\n", "copilot")
                    self.chat_display.see(tk.END)
                    self.chat_display.config(state=tk.DISABLED)
                self.root.after(0, _show_err)
                return

            # Snap Chrome window into position (below debugger bar)
            user32 = ctypes.windll.user32
            SWP_NOZORDER = 0x0004
            chrome_y = work_y + dbg_h
            chrome_h = work_h - dbg_h + 10  # +10 compensates for DPI rounding
            deadline = time.time() + 20
            while time.time() < deadline:
                hwnds = self._get_chrome_hwnds()
                if hwnds:
                    self._chrome_hwnd = next(iter(hwnds))
                    user32.SetWindowPos(self._chrome_hwnd, None, chrome_x, chrome_y, chrome_w, chrome_h, SWP_NOZORDER)
                    break
                time.sleep(0.3)
            if self._chrome_hwnd:
                time.sleep(2.0)
                user32.SetWindowPos(self._chrome_hwnd, None, chrome_x, chrome_y, chrome_w, chrome_h, SWP_NOZORDER)

            # Task loop: process automate() calls submitted by execute_strategy.
            # We poll with a short timeout instead of blocking forever so that
            # Playwright's internal event loop keeps running.  Without this,
            # CDP messages from Chrome (e.g. address-bar navigations) are never
            # processed and the omnibox appears to hang.
            while True:
                try:
                    item = self._pw_task_queue.get(timeout=0.3)
                except Exception:          # queue.Empty on timeout
                    # Pump Playwright's event loop so Chrome stays responsive
                    try:
                        self.page.evaluate("void 0")
                    except Exception:
                        pass
                    continue
                if item is None:                   # sentinel: shut down
                    break
                fn, result_q = item
                try:
                    result_q.put(("ok", fn(self.page)))
                except Exception as exc:
                    result_q.put(("err", exc))

            try:
                context.close()
                pw.stop()
            except Exception:
                pass

        self._pw_worker_thread = threading.Thread(target=_pw_worker, daemon=True)
        self._pw_worker_thread.start()

    def _reconnect_chrome(self):
        """Re-launch Chrome (called when the user clicks the Failed status label)."""
        work_x, work_y, work_w, work_h = self._work
        self._launch_shared_chrome(work_x, work_y, work_w, work_h)

    def reposition_ui(self):
        """Reposition the Tkinter window and Chrome to their initial layout.
        If Chrome was closed, re-launch it."""
        work_x, work_y, work_w, work_h = self._work
        tkinter_h = self.root.winfo_height()  # already corrected for title bar

        # Reposition Tkinter window to left half
        self.root.geometry(f"{work_w // 2}x{tkinter_h}+{work_x}+{work_y}")
        self.root.update_idletasks()
        self.left_pane.sash_place(0, 0, tkinter_h // 3)
        self.left_pane.sash_place(1, 0, (tkinter_h * 2) // 3)

        # Check if Chrome is still alive:
        # 1. The Playwright worker thread must be running
        # 2. The Chrome hwnd (if known) must still be a valid window
        user32 = ctypes.windll.user32
        SWP_NOZORDER = 0x0004
        worker_alive = (self._pw_worker_thread is not None
                        and self._pw_worker_thread.is_alive())
        hwnd_alive = (self._chrome_hwnd is not None
                      and user32.IsWindow(self._chrome_hwnd))
        chrome_alive = worker_alive and hwnd_alive

        if chrome_alive:
            # Just reposition it
            chrome_x = work_x + work_w // 2
            chrome_w = work_w - work_w // 2
            dbg_h = 90
            chrome_y = work_y + dbg_h
            chrome_h = work_h - dbg_h + 10  # +10 compensates for DPI rounding
            user32.SetWindowPos(self._chrome_hwnd, None, chrome_x, chrome_y, chrome_w, chrome_h, SWP_NOZORDER)
            # Reposition debugger window above Chrome
            if self._debugger_win:
                try:
                    self._debugger_win.geometry(f"{chrome_w}x{dbg_h}+{chrome_x}+{work_y}")
                except tk.TclError:
                    pass
        else:
            # Chrome was closed — re-launch with the persistent profile
            self._chrome_hwnd = None
            self._launch_shared_chrome(work_x, work_y, work_w, work_h)

    # ── Debugger window ──────────────────────────────────────────────
    def _show_debugger_window(self, chrome_x, chrome_y, chrome_w):
        """Create (or re-show) the debugger Toplevel above the Chrome browser."""
        if self._debugger_win is not None:
            try:
                self._debugger_win.deiconify()
                self._sync_debugger_buttons("idle")
                return
            except tk.TclError:
                pass  # window was destroyed

        dbg_h = 90
        win = tk.Toplevel(self.root)
        win.title("Debugger")
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg="#1E1E2E")
        win.geometry(f"{chrome_w - 10}x{dbg_h}+{chrome_x + 5}+{chrome_y}")
        self._debugger_win = win

        # Top row: status + buttons
        btn_frame = tk.Frame(win, bg="#1E1E2E")
        btn_frame.pack(pady=(8, 0))

        status_var = tk.StringVar(value="IDLE")
        status_lbl = tk.Label(btn_frame, textvariable=status_var,
                              font=("Consolas", 11, "bold"), fg="#666",
                              bg="#1E1E2E", width=10)
        status_lbl.pack(side=tk.LEFT, padx=(12, 8))

        btn_style = dict(
            font=("Segoe UI Emoji", 11),
            width=20,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activeforeground="white",
        )

        break_btn = tk.Button(btn_frame, text="\u23F8 Break",
                              command=self._dbg_on_break,
                              bg="#C62828", fg="white", activebackground="#E53935",
                              disabledforeground="#555",
                              state=tk.DISABLED, **btn_style)
        break_btn.pack(side=tk.LEFT, padx=4)

        continue_btn = tk.Button(btn_frame, text="\u25B6 Continue",
                                 command=self._dbg_on_continue,
                                 bg="#2E7D32", fg="white", activebackground="#43A047",
                                 disabledforeground="#555",
                                 state=tk.DISABLED, **btn_style)
        continue_btn.pack(side=tk.LEFT, padx=4)

        step_btn = tk.Button(btn_frame, text="\u23ED Step",
                             command=self._dbg_on_step,
                             bg="#1565C0", fg="white", activebackground="#1E88E5",
                             disabledforeground="#555",
                             state=tk.DISABLED, **btn_style)
        step_btn.pack(side=tk.LEFT, padx=4)

        # Bottom row: action/next-step label
        action_var = tk.StringVar(value="")
        action_lbl = tk.Label(win, textvariable=action_var,
                              font=("Consolas", 13), fg="#A0C4FF", bg="#1E1E2E",
                              anchor=tk.W)
        action_lbl.pack(fill=tk.X, padx=12, pady=(4, 6))

        self._dbg_widgets = dict(
            status_var=status_var, status_lbl=status_lbl,
            action_var=action_var,
            break_btn=break_btn, continue_btn=continue_btn,
            step_btn=step_btn,
        )
        self._sync_debugger_buttons("idle")

    def _sync_debugger_buttons(self, mode: str):
        """Sync debugger button states.  mode: 'idle' | 'running' | 'paused'."""
        w = self._dbg_widgets
        if not w:
            return
        if mode == "idle":
            w["break_btn"].config(state=tk.DISABLED, bg="#3A3A3A")
            w["continue_btn"].config(state=tk.DISABLED, bg="#3A3A3A")
            w["step_btn"].config(state=tk.DISABLED, bg="#3A3A3A")
            w["status_var"].set("IDLE")
            w["status_lbl"].config(fg="#666")
            w["action_var"].set("")
        elif mode == "running":
            w["break_btn"].config(state=tk.NORMAL, bg="#C62828")
            w["continue_btn"].config(state=tk.DISABLED, bg="#D0D0D0")
            w["step_btn"].config(state=tk.DISABLED, bg="#D0D0D0")
            w["status_var"].set("RUNNING")
            w["status_lbl"].config(fg="#4CAF50")
        elif mode == "paused":
            w["break_btn"].config(state=tk.DISABLED, bg="#3A3A3A")
            w["continue_btn"].config(state=tk.NORMAL, bg="#2E7D32")
            w["step_btn"].config(state=tk.NORMAL, bg="#1565C0")
            w["status_var"].set("PAUSED")
            w["status_lbl"].config(fg="#F44336")

    def _dbg_on_break(self):
        with _lock:
            debug_state["mode"] = "paused"
        self._sync_debugger_buttons("paused")

    def _dbg_on_continue(self):
        with _lock:
            debug_state["mode"] = "running"
        self._sync_debugger_buttons("running")
        _step_event.set()

    def _dbg_on_step(self):
        with _lock:
            debug_state["mode"] = "paused"
        _step_event.set()

    def _dbg_poll_state(self):
        """Poll debug_state from the worker thread and update the UI."""
        if self._debugger_win is None or not self._dbg_widgets:
            return
        try:
            if debug_state.get("done"):
                self._sync_debugger_buttons("idle")
                return
            mode = debug_state.get("mode", "running")
            action = debug_state.get("action", "")
            if mode == "paused":
                self._sync_debugger_buttons("paused")
                self._dbg_widgets["action_var"].set(f"Next: {action}" if action else "")
            else:
                self._sync_debugger_buttons("running")
                self._dbg_widgets["action_var"].set(f"Running: {action}" if action else "")
            self.root.after(200, self._dbg_poll_state)
        except tk.TclError:
            pass  # window destroyed

    def _get_chrome_hwnds(self) -> set:
        """Return handles of visible top-level windows owned by chrome.exe (not VS Code)."""
        user32   = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        psapi    = ctypes.windll.psapi
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        found = []

        def _cb(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True
            cls = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cls, 256)
            if cls.value != "Chrome_WidgetWin_1":
                return True
            # Get owning PID and verify the executable is chrome.exe (not code.exe etc.)
            pid = ctypes.wintypes.DWORD(0)
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            PROCESS_QUERY_INFORMATION = 0x0400
            hproc = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid.value)
            if hproc:
                exe = ctypes.create_unicode_buffer(520)
                psapi.GetModuleFileNameExW(hproc, None, exe, 520)
                kernel32.CloseHandle(hproc)
                if exe.value.lower().endswith("chrome.exe"):
                    found.append(hwnd)
            return True

        cb = WNDENUMPROC(_cb)
        user32.EnumWindows(cb, 0)
        return set(found)

    def _on_close(self):
        """Clean up shared Chrome and close the application."""
        os.environ.pop("CDP_WS_URL", None)
        # Send sentinel to stop the Playwright worker thread (it will close context/pw)
        self._pw_task_queue.put(None)
        self.root.destroy()


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
