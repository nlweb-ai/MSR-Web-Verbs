"""
Tkinter-based debugger UI for stepping through Playwright actions.

Shared state lives in the module-level dict `debug_state`.

Two modes:
  "paused"  – "Continue" and "Step" enabled; "Break" greyed out.
  "running" – only "Break" enabled; the other two greyed out.

Usage:
    from playwright_debugger import debug_state, checkpoint, run_with_debugger

    def my_automation():
        ...
        checkpoint("Navigate to example.com")
        page.goto("https://example.com")
        ...

    run_with_debugger(my_automation)
"""

import threading
import tkinter as tk

# ── Shared state (module-level) ──────────────────────────────────────
debug_state = {
    "mode": "running",     # "paused" | "running"
    "done": False,          # True when automation finishes
    "action": "",           # description of the next action
}

_step_event = threading.Event()
_lock = threading.Lock()
_root: tk.Tk | None = None
_widgets: dict = {}


# ── UI construction ──────────────────────────────────────────────────
def _create_ui():
    global _root
    root = tk.Tk()
    root.title("Playwright Debugger")
    root.geometry("620x180")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    _root = root

    status_var = tk.StringVar(value="PAUSED")
    status_lbl = tk.Label(root, textvariable=status_var,
                          font=("Consolas", 13, "bold"), fg="red")
    status_lbl.pack(pady=(10, 2))

    action_var = tk.StringVar(value="(waiting for first action)")
    tk.Label(root, textvariable=action_var,
             font=("Consolas", 10), wraplength=500,
             justify=tk.LEFT).pack(pady=(0, 8))

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=6)

    # Unicode icons for debugger buttons
    break_btn = tk.Button(btn_frame, text="\u23F8 Break",
                          command=_on_break, width=14, font=("Segoe UI Emoji", 10))
    break_btn.grid(row=0, column=0, padx=4)

    continue_btn = tk.Button(btn_frame, text="\u25B6 Continue",
                             command=_on_continue, width=14, font=("Segoe UI Emoji", 10))
    continue_btn.grid(row=0, column=1, padx=4)

    step_btn = tk.Button(btn_frame, text="\u23ED Step",
                         command=_on_step, width=14, font=("Segoe UI Emoji", 10))
    step_btn.grid(row=0, column=2, padx=4)

    _widgets.update(
        status_var=status_var, status_lbl=status_lbl,
        action_var=action_var,
        break_btn=break_btn, continue_btn=continue_btn,
        step_btn=step_btn,
    )
    _sync_buttons()


# ── Button state sync ───────────────────────────────────────────────
def _sync_buttons():
    if debug_state["mode"] == "running":
        _widgets["break_btn"].config(state=tk.NORMAL)
        _widgets["continue_btn"].config(state=tk.DISABLED)
        _widgets["step_btn"].config(state=tk.DISABLED)
        _widgets["status_var"].set("RUNNING")
        _widgets["status_lbl"].config(fg="green")
    else:
        _widgets["break_btn"].config(state=tk.DISABLED)
        _widgets["continue_btn"].config(state=tk.NORMAL)
        _widgets["step_btn"].config(state=tk.NORMAL)
        _widgets["status_var"].set("PAUSED")
        _widgets["status_lbl"].config(fg="red")


# ── Button handlers ─────────────────────────────────────────────────
def _on_break():
    with _lock:
        debug_state["mode"] = "paused"
    _sync_buttons()


def _on_continue():
    with _lock:
        debug_state["mode"] = "running"
    _sync_buttons()
    _step_event.set()


def _on_step():
    with _lock:
        debug_state["mode"] = "paused"
    _step_event.set()


# ── Checkpoint (called from worker thread before each action) ────────
def checkpoint(description: str):
    """Block if paused; pass through if running."""
    if debug_state["done"]:
        return

    debug_state["action"] = description

    with _lock:
        paused = debug_state["mode"] == "paused"

    if paused:
        _step_event.clear()
        if _root:
            _root.after(0, lambda: _widgets["action_var"].set(f"Next: {description}"))
            _root.after(0, _sync_buttons)
        _step_event.wait()
    else:
        if _root:
            _root.after(0, lambda: _widgets["action_var"].set(f"Running: {description}"))


# ── Entry point ─────────────────────────────────────────────────────
def run_with_debugger(target_func, *args, **kwargs):
    """Run *target_func* in a background thread; Tk mainloop on main thread."""
    _create_ui()

    def _worker():
        try:
            target_func(*args, **kwargs)
        finally:
            debug_state["done"] = True
            _step_event.set()
            if _root:
                _root.after(0, _root.destroy)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    _root.mainloop()
    t.join(timeout=5)
