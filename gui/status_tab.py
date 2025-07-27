import tkinter as tk
from tkinter import ttk
from datetime import datetime
from theme.windows98 import WIN98_COLORS, WIN98_FONT, WIN98_TITLE_FONT

class StatusTab(tk.Frame):  # Use tk.Frame for classic Win98 look
    """
    Tab widget to display scanner status in a grid layout with a green progress bar.
    Consistent Win98 styling and layout.
    """
    def __init__(self, parent, theme_controller=None, **kwargs):
        super().__init__(parent, borderwidth=4, relief="solid")
        self.theme_controller = theme_controller
        self.state_var = tk.StringVar(value="IDLE")
        self.last_scan_var = tk.StringVar(value="NEVER")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.version_var = tk.StringVar(value="1.0.0")
        self.db_freshness_var = tk.StringVar(value="UP-TO-DATE")
        self._build_ui()

    def _build_ui(self):
        # Main panel with consistent outer padding and grooved border (no black border)
        frame = tk.Frame(self, bg=WIN98_COLORS['panel'], borderwidth=2, relief='groove', highlightthickness=0)
        frame.pack(expand=True, fill='both', padx=24, pady=24)
        # Section heading
        heading = tk.Label(frame, text="Status", font=WIN98_TITLE_FONT, fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['panel'], pady=8)  # Bold, large heading
        heading.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 16))
        frame.grid_columnconfigure(1, weight=1)
        # Status fields (all uppercase)
        label_defs = [
            ("CURRENT STATE", self.state_var),
            ("LAST SCAN", self.last_scan_var),
            ("SCANNER VERSION", self.version_var),
            ("DATABASE STATUS", self.db_freshness_var)
        ]
        for i, (label, var) in enumerate(label_defs, start=1):
            lbl = tk.Label(frame, text=label, font=WIN98_FONT, fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['panel'])
            lbl.grid(row=i, column=0, sticky="w", padx=(0, 20), pady=12)
            val = tk.Label(frame, textvariable=var, font=WIN98_FONT, fg=WIN98_COLORS['text'], bg=WIN98_COLORS['panel'], borderwidth=0, relief='flat')
            val.grid(row=i, column=1, sticky="w", pady=12)
        # Progress bar label and bar
        prog_lbl = tk.Label(frame, text="SCAN PROGRESS", font=WIN98_FONT, fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['panel'])
        prog_lbl.grid(row=5, column=0, sticky="w", padx=(0, 20), pady=12)
        progressbar = ttk.Progressbar(frame, variable=self.progress_var, maximum=100, length=220, style="Win98.Horizontal.TProgressbar")
        progressbar.grid(row=5, column=1, sticky="w", pady=12)

    def update_status(self, state=None, last_scan=None, progress=None, version=None, db_freshness=None):
        """Update the displayed status values. All values are set to uppercase."""
        if state is not None:
            self.state_var.set(str(state).upper())
        if last_scan is not None:
            self.last_scan_var.set(str(last_scan).upper())
        if progress is not None:
            self.progress_var.set(progress)
        if version is not None:
            self.version_var.set(str(version).upper())
        if db_freshness is not None:
            self.db_freshness_var.set(str(db_freshness).upper())

# Test block for standalone run/demo
'''
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scanner Status Demo")
    notebook = ttk.Notebook(root)
    status_tab = StatusTab(notebook)
    notebook.add(status_tab, text="Scanner Status")
    notebook.pack(expand=True, fill="both")
    import time
    def simulate():
        status_tab.update_status(state="Scanning", last_scan=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), progress=0, version="1.2.3", db_freshness="Up-to-date")
        for i in range(101):
            status_tab.update_status(progress=i)
            root.update()
            time.sleep(0.02)
        status_tab.update_status(state="Idle", db_freshness="Stale")
    root.after(1000, simulate)
    root.mainloop()
'''