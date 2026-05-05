"""
macOS port of app.py — Mac-compatible entry point for the Browser Agent UI.

Differences from app.py:
- No ctypes/windll/wintypes (Windows-only). Window positioning is done via
  tkinter's screen-info APIs and Chrome's own --window-position/--window-size
  args; we drop the post-launch SetWindowPos snap loop.
- Chrome profile path uses ~/Library/Application Support/Google/Chrome
  instead of %LOCALAPPDATA%\\Google\\Chrome.
- Chrome process kill uses pkill/pgrep instead of taskkill/tasklist.
- _get_chrome_hwnds is removed; "Chrome alive" check is just worker-thread alive.

All other logic — refine/strategize/code-gen/execute pipeline, debugger window,
worker thread, profile bootstrap — is identical to app.py.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
import queue
import sys
import threading
import time
import subprocess
import shutil

# Add the UI directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Add verbs directory for cdp_utils
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "verbs"))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import debug_state, _step_event, _lock, StopExecution

from file_loader import load_files_as_tabs
from event_handlers import update_highest_version, handle_task_tab_changed, handle_strategy_tab_changed
from action_handlers import submit_message, open_task, create_task, generate_strategy, execute_strategy, save_task, preview_task, modify_task

# ── Mac-port patch: drop hardcoded --model flag ──────────────────────────────
# Shuo's copilot.py hardcodes "claude-sonnet-4.6" / "claude-haiku-4.5" but the
# stock GitHub Copilot CLI we just installed via npm doesn't recognize those
# names ("Model X is not available"). Letting the CLI use its server-side
# default works fine, so we override DEFAULT_MODEL / CODE_SUMMARY_MODEL to "".
# `if model:` inside copilot.py then skips emitting the flag.
import copilot as _copilot_mod
import action_handlers as _ah_mod
_copilot_mod.DEFAULT_MODEL = ""
_copilot_mod.CODE_SUMMARY_MODEL = ""
# The default arg of copilot_stream/copilot() captured DEFAULT_MODEL at def-time,
# so we also overwrite their __defaults__ tuple. Tuple shape: (cwd, model).
_copilot_mod.copilot_stream.__defaults__ = (None, "")
_copilot_mod.copilot.__defaults__ = (None, "")
# action_handlers imported CODE_SUMMARY_MODEL by name, so re-bind that too.
_ah_mod.CODE_SUMMARY_MODEL = ""

# ── Mac-port patch: force non-interactive Copilot CLI mode ───────────────────
# The new GitHub Copilot CLI defaults to interactive (asks for confirmations).
# Without --allow-all-tools / --allow-all-paths it refuses to write files,
# so Code_NNNN.py ends up containing chat reasoning instead of Python.
# We wrap copilot_stream and copilot() to always inject those flags.
_orig_copilot_stream = _copilot_mod.copilot_stream
_orig_copilot_fn     = _copilot_mod.copilot

def _copilot_stream_allow_all(prompt, cwd=None, model="", *extra):
    flags = ("--allow-all-tools", "--allow-all-paths")
    yield from _orig_copilot_stream(prompt, cwd, model, *(flags + tuple(extra)))

def _copilot_fn_allow_all(prompt, cwd=None, model="", *extra):
    flags = ("--allow-all-tools", "--allow-all-paths")
    return _orig_copilot_fn(prompt, cwd, model, *(flags + tuple(extra)))

_copilot_mod.copilot_stream = _copilot_stream_allow_all
_copilot_mod.copilot = _copilot_fn_allow_all
# action_handlers also imported copilot_stream by name; re-bind that too.
_ah_mod.copilot_stream = _copilot_stream_allow_all
# ────────────────────────────────────────────────────────────────────────────


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
    """Main application class for the chat interface (macOS variant)."""

    def __init__(self, root):
        self.root = root
        self.root.title("Browser Agent Based On Web Verbs (macOS)")

        # Set workspace path for copilot commands
        self.workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Read task_name from cache.txt or use default
        cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache.txt")
        try:
            with open(cache_file, 'r') as f:
                self.task_name = f.read().strip()
                if not self.task_name:
                    self.task_name = "2026-01-12"
        except FileNotFoundError:
            self.task_name = "2026-01-12"

        self.case_dir = os.path.join(self.workspace_path, "tasks", self.task_name)

        # Shared Chrome browser state
        self.chrome_ws_url = None
        self.chrome_proc = None
        self.chrome_profile_dir = None
        self._chrome_hwnd = None  # unused on Mac, kept for API compatibility
        self._chrome_debug_port = None
        self._pw_task_queue = queue.SimpleQueue()
        self._pw_worker_thread = None
        self.page = None
        self._stop_requested = False
        self._work = (0, 0, 0, 0)
        self._debugger_win = None
        self._dbg_widgets = {}

        self._configure_styles()
        self._create_ui()
        self._load_initial_data()

        # Get usable working area via tkinter (Mac equivalent of SystemParametersInfoW).
        # tkinter doesn't exclude the menu bar / dock, so we add a conservative inset.
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        MAC_MENUBAR_H = 28   # menu bar
        MAC_DOCK_INSET = 80  # rough dock reserve at the bottom
        work_x = 0
        work_y = MAC_MENUBAR_H
        work_w = screen_w
        work_h = screen_h - MAC_MENUBAR_H - MAC_DOCK_INSET

        self._work = (work_x, work_y, work_w, work_h)

        # Position tkinter window on the left half of the working area.
        self.root.geometry(f"{work_w // 2}x{work_h}+{work_x}+{work_y}")
        self.root.update_idletasks()
        title_bar_h = self.root.winfo_rooty() - work_y
        if title_bar_h < 0:
            title_bar_h = 22  # macOS default title bar height fallback
        tkinter_h = work_h - title_bar_h
        self.root.geometry(f"{work_w // 2}x{tkinter_h}+{work_x}+{work_y}")
        self.root.update_idletasks()

        self.left_pane.sash_place(0, 0, tkinter_h // 3)
        self.left_pane.sash_place(1, 0, (tkinter_h * 2) // 3)

        self.input_box.insert(0, "")

        # Launch shared Chrome on the right half
        self._launch_shared_chrome(work_x, work_y, work_w, work_h, title_bar_h)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 12))
        style.map('TNotebook.Tab',
                 background=[('selected', '#4CAF50'), ('!selected', '#E0E0E0')],
                 foreground=[('selected', 'white'), ('!selected', 'black')],
                 font=[('selected', ('Arial', 12, 'bold')), ('!selected', ('Arial', 12))])
        style.configure('Strategies.TNotebook.Tab', padding=[10, 5], font=('Arial', 12))
        style.map('Strategies.TNotebook.Tab',
                 background=[('selected', '#F57C00'), ('!selected', '#E0E0E0')],
                 foreground=[('selected', 'white'), ('!selected', 'black')],
                 font=[('selected', ('Arial', 12, 'bold')), ('!selected', ('Arial', 12))])

    def _create_ui(self):
        self._create_control_panel()
        self.left_pane = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=5)
        self.left_pane.pack(fill=tk.BOTH, expand=True)
        self._create_chat_pane(self.left_pane)
        self._create_tasks_pane(self.left_pane)
        self._create_strategies_pane(self.left_pane)

    def _create_control_panel(self):
        panel = tk.Frame(self.root, bg="#ECECEC", relief=tk.GROOVE, borderwidth=1)
        panel.pack(fill=tk.X, side=tk.TOP)
        right_frame = tk.Frame(panel, bg="#ECECEC")
        right_frame.pack(side=tk.RIGHT, padx=8, pady=4)
        self._chrome_status_label = tk.Label(
            right_frame,
            text="Chrome: ⏳ Connecting...",
            bg="#ECECEC", fg="#888", font=("Arial", 10),
            cursor="hand2"
        )
        self._chrome_status_label.pack(side=tk.RIGHT, padx=(0, 12))
        self._chrome_status_label.bind("<Button-1>", lambda _e: self._reconnect_chrome())

    def _create_tasks_pane(self, parent):
        upper_left = tk.Frame(parent, bg="white", relief=tk.RIDGE, borderwidth=2)
        parent.add(upper_left)
        tasks_header_frame = tk.Frame(upper_left, bg="#2E7D32")
        tasks_header_frame.pack(fill=tk.X)
        tasks_label = tk.Label(tasks_header_frame, text="Tasks", bg="#2E7D32", fg="white",
                               font=("Arial", 13, "bold"))
        tasks_label.pack(side=tk.LEFT, padx=8, pady=4)
        tasks_button_frame = tk.Frame(tasks_header_frame, bg="#2E7D32")
        tasks_button_frame.pack(side=tk.RIGHT, padx=5)
        preview_task_button = tk.Button(
            tasks_button_frame, text="\U0001F441",
            command=lambda: preview_task(self),
            bg="#43A047", fg="white", font=("Arial", 14),
            padx=4, pady=2, relief=tk.RAISED, bd=2, cursor="hand2"
        )
        preview_task_button.pack(side=tk.LEFT, padx=(0, 4))
        _add_tooltip(preview_task_button, "Render Markdown")
        self.save_task_button = tk.Button(
            tasks_button_frame, text="\U0001F4BE",
            command=lambda: save_task(self),
            bg="#43A047", fg="white", font=("Arial", 14),
            padx=4, pady=2, relief=tk.RAISED, bd=2, cursor="hand2"
        )
        _add_tooltip(self.save_task_button, "Save")
        self.generate_strategy_button = tk.Button(
            tasks_button_frame, text="\U0001F9E9",
            command=lambda: generate_strategy(self),
            bg="#E65100", fg="white", font=("Arial", 16),
            padx=4, pady=2, relief=tk.RAISED, bd=2, cursor="hand2"
        )
        _add_tooltip(self.generate_strategy_button, "Generate Strategy")
        self.tasks_notebook = ttk.Notebook(upper_left)
        self.tasks_notebook.pack(fill=tk.BOTH, expand=True)
        self.tasks_notebook.bind("<<NotebookTabChanged>>", lambda e: handle_task_tab_changed(self, e))

    def _create_strategies_pane(self, parent):
        lower_left = tk.Frame(parent, bg="white", relief=tk.RIDGE, borderwidth=2)
        parent.add(lower_left)
        strategies_header_frame = tk.Frame(lower_left, bg="#E65100")
        strategies_header_frame.pack(fill=tk.X)
        strategies_label = tk.Label(strategies_header_frame, text="Strategies", bg="#E65100", fg="white",
                                    font=("Arial", 13, "bold"))
        strategies_label.pack(side=tk.LEFT, padx=8, pady=4)
        strategies_button_frame = tk.Frame(strategies_header_frame, bg="#E65100")
        strategies_button_frame.pack(side=tk.RIGHT, padx=5)
        self.execute_button = tk.Button(
            strategies_button_frame, text="▶",
            command=lambda: execute_strategy(self),
            bg="#2E7D32", fg="white", font=("Arial", 16),
            padx=4, pady=2, relief=tk.RAISED, bd=2, cursor="hand2"
        )
        _add_tooltip(self.execute_button, "Execute")
        self.strategies_notebook = ttk.Notebook(lower_left, style='Strategies.TNotebook')
        self.strategies_notebook.pack(fill=tk.BOTH, expand=True)
        self.strategies_notebook.bind("<<NotebookTabChanged>>", lambda e: handle_strategy_tab_changed(self, e))

    def _create_chat_pane(self, parent):
        chat_pane = tk.Frame(parent, bg="white", relief=tk.RIDGE, borderwidth=2)
        parent.add(chat_pane)
        chat_header = tk.Frame(chat_pane, bg="#1565C0")
        chat_header.pack(fill=tk.X)
        tk.Label(chat_header, text="Chat", bg="#1565C0", fg="white",
                 font=("Arial", 13, "bold")).pack(side=tk.LEFT, padx=8, pady=4)
        task_control_frame = tk.Frame(chat_pane)
        task_control_frame.pack(fill=tk.X, padx=5, pady=5)
        task_label = tk.Label(task_control_frame, text="Task Name:", font=("Arial", 12))
        task_label.pack(side=tk.LEFT, padx=(0, 5))
        tasks_root = os.path.join(self.workspace_path, "tasks")
        try:
            task_folders = sorted(
                [d for d in os.listdir(tasks_root)
                 if os.path.isdir(os.path.join(tasks_root, d)) and d != "sample"],
                reverse=True
            )
        except FileNotFoundError:
            task_folders = []
        self.task_name_input = ttk.Combobox(
            task_control_frame, values=task_folders, font=("Arial", 12), state="readonly"
        )
        self.task_name_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        if self.task_name in task_folders:
            self.task_name_input.current(task_folders.index(self.task_name))
        elif task_folders:
            self.task_name_input.current(0)
        self.task_name_input.bind("<<ComboboxSelected>>", lambda e: open_task(self))
        reposition_btn = tk.Button(
            task_control_frame, text="♻",
            command=lambda: self.reposition_ui(),
            bg="#AB47BC", fg="white", font=("Arial", 14),
            padx=4, pady=2, relief=tk.RAISED, bd=2, cursor="hand2"
        )
        reposition_btn.pack(side=tk.RIGHT)
        _add_tooltip(reposition_btn, "Reposition UI")
        create_task_btn = tk.Button(
            task_control_frame, text="✨",
            command=lambda: create_task(self),
            bg="#AB47BC", fg="white", font=("Arial", 14),
            padx=4, pady=2, relief=tk.RAISED, bd=2, cursor="hand2"
        )
        create_task_btn.pack(side=tk.RIGHT)
        _add_tooltip(create_task_btn, "Create Task")
        chat_frame = tk.Frame(chat_pane)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, width=40, height=5,
            state=tk.DISABLED, bg="white", font=("Arial", 12)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.tag_config("user", foreground="green")
        self.chat_display.tag_config("copilot", foreground="blue")
        self.chat_display.tag_config("error", foreground="red")
        input_frame = tk.Frame(chat_pane)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        self.input_box = tk.Entry(input_frame, font=("Arial", 12))
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.input_box.bind("<Return>", lambda event: submit_message(self))
        new_button = tk.Button(
            input_frame, text="➕",
            command=lambda: self._clear_chat(),
            bg="#42A5F5", fg="white", font=("Arial", 14),
            padx=4, pady=2, relief=tk.RAISED, bd=2, cursor="hand2"
        )
        new_button.pack(side=tk.RIGHT)
        _add_tooltip(new_button, "New Chat")
        modify_task_button = tk.Button(
            input_frame, text="\U0001F4DD",
            command=lambda: modify_task(self),
            bg="#66BB6A", fg="white", font=("Arial", 14),
            padx=4, pady=2, relief=tk.RAISED, bd=2, cursor="hand2"
        )
        modify_task_button.pack(side=tk.RIGHT)
        _add_tooltip(modify_task_button, "Modify Task")
        submit_button = tk.Button(
            input_frame, text="\U0001F4AC",
            command=lambda: submit_message(self),
            bg="#42A5F5", fg="white", font=("Arial", 14),
            padx=4, pady=2, relief=tk.RAISED, bd=2, cursor="hand2"
        )
        submit_button.pack(side=tk.RIGHT)
        _add_tooltip(submit_button, "Ask")

    def _load_initial_data(self):
        load_files_as_tabs(self, self.tasks_notebook, "task-*.md")
        self.highest_task_version = update_highest_version(self.tasks_notebook, 'highest_task_version')
        load_files_as_tabs(self, self.strategies_notebook, "strategy-*.md")
        self.highest_strategy_version = update_highest_version(self.strategies_notebook, 'highest_strategy_version')
        handle_task_tab_changed(self)
        handle_strategy_tab_changed(self)

    def _clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _kill_all_chrome(self):
        """Kill all running Chrome processes (Mac equivalent of taskkill)."""
        try:
            subprocess.run(
                ["pkill", "-f", "Google Chrome"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
        # Poll until pgrep confirms no Chrome remains (up to 8 seconds)
        deadline = time.time() + 8.0
        while time.time() < deadline:
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "Google Chrome"],
                    capture_output=True, text=True
                )
                if not result.stdout.strip():
                    break
            except Exception:
                break
            time.sleep(0.5)
        # Extra buffer for profile lock release
        time.sleep(1.5)

    def _reset_chrome_crash_flag(self, user_data_dir: str):
        """Clear Chrome's crash-recovery flags and stale lock files."""
        for lock_rel in [
            "lockfile",
            os.path.join("Default", "lockfile"),
            os.path.join("Default", "SingletonLock"),
            "SingletonLock",       # Mac uses these at the User Data root
            "SingletonCookie",
            "SingletonSocket",
        ]:
            lock_path = os.path.join(user_data_dir, lock_rel)
            try:
                if os.path.lexists(lock_path):
                    os.remove(lock_path)
            except Exception:
                pass

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
        """Launch Chrome via a persistent Playwright worker thread (Mac variant)."""
        chrome_x = work_x + work_w // 2
        chrome_w = work_w - work_w // 2
        dbg_h = 90

        if self._pw_worker_thread is not None and self._pw_worker_thread.is_alive():
            self._pw_task_queue.put(None)
            self._pw_worker_thread.join(timeout=10)
        self._pw_task_queue = queue.SimpleQueue()
        self.page = None

        # Mac doesn't have the same DPI scaling quirk as the Windows version,
        # so use a 1.0 scale factor and pass raw pixel coords.
        chrome_y = work_y + dbg_h
        chrome_h = work_h - dbg_h

        # Mac Chrome profile location
        home = os.path.expanduser("~")
        chrome_root  = os.path.join(home, "Library", "Application Support", "Google", "Chrome")
        real_default = os.path.join(chrome_root, "Default")
        # Use a separate profile for Playwright (Chrome forbids CDP on the real default)
        pw_profile   = os.path.join(chrome_root, "Playwright User Data")
        pw_default   = os.path.join(pw_profile, "Default")

        self.root.after(0, lambda: self._chrome_status_label.config(
            text="Chrome: ⏳ Launching...", fg="#888"))

        def _pw_worker():
            self._kill_all_chrome()

            # First-time setup: copy login data from real profile
            if not os.path.isdir(pw_default):
                os.makedirs(pw_default, exist_ok=True)

                # Local State at the root (contains the encryption key for Cookies)
                for fname in ["Local State"]:
                    src = os.path.join(chrome_root, fname)
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
                        f"--window-position={chrome_x},{chrome_y}",
                        f"--window-size={chrome_w},{chrome_h}",
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-infobars",
                    ]
                )
                self.page = context.new_page()
                self.root.after(0, lambda: self._chrome_status_label.config(
                    text="Chrome: ✅ Connected", fg="#060"))
                self.root.after(0, lambda: self._show_debugger_window(chrome_x, work_y, chrome_w))
            except Exception as exc:
                err_msg = str(exc)
                def _show_err():
                    self._chrome_status_label.config(
                        text="Chrome: ❌ Failed (click to retry)", fg="#c00")
                    self.chat_display.config(state=tk.NORMAL)
                    self.chat_display.insert(
                        tk.END, f"⚠️ Chrome launch failed: {err_msg}\n\n", "copilot")
                    self.chat_display.see(tk.END)
                    self.chat_display.config(state=tk.DISABLED)
                self.root.after(0, _show_err)
                return

            # Mac: skip the Windows SetWindowPos snap loop; Chrome already
            # honored --window-position/--window-size at launch.

            # Task loop
            while True:
                try:
                    item = self._pw_task_queue.get(timeout=0.3)
                except Exception:
                    try:
                        self.page.evaluate("void 0")
                    except Exception:
                        pass
                    continue
                if item is None:
                    break
                fn, result_q = item
                try:
                    result_q.put(("ok", fn(self.page)))
                except StopExecution:
                    result_q.put(("stopped", "Stopped by user"))
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
        work_x, work_y, work_w, work_h = self._work
        self._launch_shared_chrome(work_x, work_y, work_w, work_h)

    def reposition_ui(self):
        """Reposition the tkinter window to its initial layout. If Chrome was
        closed, re-launch it. Mac note: we can't programmatically reposition
        an external Chrome window, so on Mac the chrome side stays where the
        user left it (only the tkinter window snaps back)."""
        work_x, work_y, work_w, work_h = self._work
        tkinter_h = self.root.winfo_height()
        self.root.geometry(f"{work_w // 2}x{tkinter_h}+{work_x}+{work_y}")
        self.root.update_idletasks()
        self.left_pane.sash_place(0, 0, tkinter_h // 3)
        self.left_pane.sash_place(1, 0, (tkinter_h * 2) // 3)

        # On Mac, "is Chrome alive" reduces to "is the playwright worker alive"
        worker_alive = (self._pw_worker_thread is not None
                        and self._pw_worker_thread.is_alive())
        if not worker_alive:
            self._launch_shared_chrome(work_x, work_y, work_w, work_h)

    # ── Debugger window ──────────────────────────────────────────────
    def _show_debugger_window(self, chrome_x, chrome_y, chrome_w):
        if self._debugger_win is not None:
            try:
                self._debugger_win.deiconify()
                self._sync_debugger_buttons("idle")
                return
            except tk.TclError:
                pass

        dbg_h = 90
        win = tk.Toplevel(self.root)
        win.title("Debugger")
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg="#1E1E2E")
        win.geometry(f"{chrome_w - 10}x{dbg_h}+{chrome_x + 5}+{chrome_y}")
        self._debugger_win = win

        btn_frame = tk.Frame(win, bg="#1E1E2E")
        btn_frame.pack(pady=(8, 0))

        status_var = tk.StringVar(value="IDLE")
        status_lbl = tk.Label(btn_frame, textvariable=status_var,
                              font=("Consolas", 11, "bold"), fg="#666",
                              bg="#1E1E2E", width=10)
        status_lbl.pack(side=tk.LEFT, padx=(12, 8))

        btn_style = dict(
            font=("Apple Color Emoji", 11),  # macOS emoji font
            width=20,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activeforeground="white",
        )

        break_btn = tk.Button(btn_frame, text="⏸ Break",
                              command=self._dbg_on_break,
                              bg="#C62828", fg="white", activebackground="#E53935",
                              disabledforeground="#555",
                              state=tk.DISABLED, **btn_style)
        break_btn.pack(side=tk.LEFT, padx=4)

        continue_btn = tk.Button(btn_frame, text="▶ Continue",
                                 command=self._dbg_on_continue,
                                 bg="#2E7D32", fg="white", activebackground="#43A047",
                                 disabledforeground="#555",
                                 state=tk.DISABLED, **btn_style)
        continue_btn.pack(side=tk.LEFT, padx=4)

        step_btn = tk.Button(btn_frame, text="⏭ Step",
                             command=self._dbg_on_step,
                             bg="#1565C0", fg="white", activebackground="#1E88E5",
                             disabledforeground="#555",
                             state=tk.DISABLED, **btn_style)
        step_btn.pack(side=tk.LEFT, padx=4)

        stop_btn = tk.Button(btn_frame, text="⏹ Stop",
                             command=self._dbg_on_stop,
                             bg="#B71C1C", fg="white", activebackground="#D32F2F",
                             disabledforeground="#555",
                             state=tk.DISABLED, **btn_style)
        stop_btn.pack(side=tk.LEFT, padx=4)

        action_var = tk.StringVar(value="")
        action_lbl = tk.Label(win, textvariable=action_var,
                              font=("Consolas", 13), fg="#A0C4FF", bg="#1E1E2E",
                              anchor=tk.W)
        action_lbl.pack(fill=tk.X, padx=12, pady=(4, 6))

        self._dbg_widgets = dict(
            status_var=status_var, status_lbl=status_lbl,
            action_var=action_var,
            break_btn=break_btn, continue_btn=continue_btn,
            step_btn=step_btn, stop_btn=stop_btn,
        )
        self._sync_debugger_buttons("idle")

    def _sync_debugger_buttons(self, mode: str):
        w = self._dbg_widgets
        if not w:
            return
        if mode == "idle":
            w["break_btn"].config(state=tk.DISABLED, bg="#3A3A3A")
            w["continue_btn"].config(state=tk.DISABLED, bg="#3A3A3A")
            w["step_btn"].config(state=tk.DISABLED, bg="#3A3A3A")
            w["stop_btn"].config(state=tk.DISABLED, bg="#3A3A3A")
            w["status_var"].set("IDLE")
            w["status_lbl"].config(fg="#666")
            w["action_var"].set("")
        elif mode == "running":
            w["break_btn"].config(state=tk.NORMAL, bg="#C62828")
            w["continue_btn"].config(state=tk.DISABLED, bg="#D0D0D0")
            w["step_btn"].config(state=tk.DISABLED, bg="#D0D0D0")
            w["stop_btn"].config(state=tk.NORMAL, bg="#B71C1C")
            w["status_var"].set("RUNNING")
            w["status_lbl"].config(fg="#4CAF50")
        elif mode == "paused":
            w["break_btn"].config(state=tk.DISABLED, bg="#3A3A3A")
            w["continue_btn"].config(state=tk.NORMAL, bg="#2E7D32")
            w["step_btn"].config(state=tk.NORMAL, bg="#1565C0")
            w["stop_btn"].config(state=tk.NORMAL, bg="#B71C1C")
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

    def _dbg_on_stop(self):
        self._stop_requested = True
        with _lock:
            debug_state["stop"] = True
            debug_state["mode"] = "running"
        _step_event.set()
        self._sync_debugger_buttons("idle")
        self._dbg_widgets["action_var"].set("Stopped")

    def _dbg_poll_state(self):
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
            pass

    def _on_close(self):
        os.environ.pop("CDP_WS_URL", None)
        self._pw_task_queue.put(None)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
