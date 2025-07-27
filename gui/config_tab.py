import tkinter as tk
from tkinter import ttk, messagebox
from theme.windows98 import WIN98_COLORS, WIN98_FONT, WIN98_TITLE_FONT
from gui.tooltip import Tooltip  # Add this import

class ConfigTab(ttk.Frame):
    """
    Configuration tab: allows editing settings, including the website URL and dashboard API for sharing.
    """
    def __init__(self, parent, service, on_theme_change=None, theme_controller=None):
        super().__init__(parent)
        self.service = service
        self.on_theme_change = on_theme_change
        self.theme_controller = theme_controller
        self.apply_theme()
        self._build_ui()

    def apply_theme(self):
        if self.theme_controller:
            self.theme_controller.apply_config_tab_theme(self)
        else:
            # fallback to modern dashboard
            self['background'] = WIN98_COLORS['bg']

    def _build_ui(self):
        config = self.service.get_config()
        # Main container with Win98 bg and extra padding
        frame = tk.Frame(self, bg=WIN98_COLORS['panel'], padx=24, pady=24, borderwidth=2, relief='groove', highlightbackground=WIN98_COLORS['button_border'], highlightthickness=1)
        frame.pack(expand=True, fill='both', padx=24, pady=24)  # Consistent outer padding
        # Section heading
        heading = tk.Label(frame, text="Configuration", font=WIN98_TITLE_FONT, fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['panel'], pady=8)  # Bold, large heading
        heading.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 16))
        # Website URL
        url_label = tk.Label(frame, text="Website URL (HTTPS):", font=WIN98_FONT, fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['panel'])
        url_label.grid(row=1, column=0, sticky='e', padx=(0, 20), pady=12)
        self.url_var = tk.StringVar(value=config.remote_url)
        url_entry = ttk.Entry(frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=1, column=1, sticky='w', pady=12)
        url_entry.configure(style='Win98.TEntry')
        # Save button centered at the bottom
        save_btn = ttk.Button(frame, text="Save", command=self._on_save, style='Win98.TButton')
        save_btn.grid(row=3, column=0, columnspan=3, pady=(32, 0), sticky='ew')  # Centered at bottom
        Tooltip(save_btn, text="Save your configuration changes.")

    def _on_save(self):
        url = self.url_var.get().strip()
        if url and not url.lower().startswith('https://'):
            messagebox.showerror("Invalid URL", "Please enter a valid HTTPS Website URL.")
            return
        self.service.update_config(remote_url=url)
        messagebox.showinfo("Configuration", "Settings saved.") 