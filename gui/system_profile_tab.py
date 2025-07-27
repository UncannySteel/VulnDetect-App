import tkinter as tk
from tkinter import ttk
from theme.windows98 import WIN98_COLORS, WIN98_FONT, WIN98_TITLE_FONT

class SystemProfileTab(ttk.Frame):
    """
    Tab for displaying system profile info in a grid with a consistent border.
    """
    def __init__(self, parent, profile_data=None, theme_controller=None, *args, **kwargs):
        super().__init__(parent, borderwidth=4, relief="solid")
        self.profile_data = profile_data or {}
        self.theme_controller = theme_controller
        self.apply_theme()
        self._build_ui()

    def apply_theme(self):
        if hasattr(self, 'theme_controller') and self.theme_controller:
            self.theme_controller.apply_system_profile_tab_theme(self)
        else:
            self['background'] = WIN98_COLORS['bg']
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Profile.TLabel', background=WIN98_COLORS['panel'], foreground=WIN98_COLORS['accent'], font=WIN98_FONT)
        style.configure('ProfileValue.TLabel', background=WIN98_COLORS['panel'], foreground=WIN98_COLORS['text'], font=WIN98_FONT)
        style.configure('TabFrame.TFrame', background=WIN98_COLORS['panel'], borderwidth=2, relief='groove')

    def _build_ui(self):
        # Main panel with consistent outer padding
        frame = tk.Frame(self, bg=WIN98_COLORS['panel'], borderwidth=2, relief='groove', highlightbackground=WIN98_COLORS['button_border'], highlightthickness=1)
        frame.pack(expand=True, fill='both', padx=24, pady=24)
        heading = tk.Label(frame, text="System Profile", font=WIN98_TITLE_FONT, fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['panel'], pady=8)  # Bold, large heading
        heading.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 16))
        frame.grid_columnconfigure(1, weight=1)
        labels = [
            ("OS NAME", self.profile_data.get('os_name', '').upper()),
            ("OS VERSION", self.profile_data.get('os_version', '').upper()),
            ("ARCHITECTURE", self.profile_data.get('architecture', '').upper()),
            ("KERNEL VERSION", self.profile_data.get('kernel_version', '').upper()),
        ]
        for i, (label, value) in enumerate(labels, start=1):
            lbl = ttk.Label(frame, text=label, style='Profile.TLabel')
            lbl.grid(row=i, column=0, sticky='e', padx=(0, 20), pady=12)  # Consistent inner spacing
            val = ttk.Label(frame, text=value, style='ProfileValue.TLabel')
            val.grid(row=i, column=1, sticky='w', pady=12)
        comp_lbl = ttk.Label(frame, text="KEY COMPONENTS", style='Profile.TLabel')
        comp_lbl.grid(row=len(labels)+1, column=0, sticky='ne', padx=(0, 20), pady=12)
        components = self.profile_data.get('components', {})
        comp_text = "\n".join(
            f"• {k.upper()}: {v.upper()}"
            for k, v in components.items()
            if v and v.strip().upper() != 'UNKNOWN'
        )
        comp_val = ttk.Label(frame, text=comp_text, style='ProfileValue.TLabel', justify='left')
        comp_val.grid(row=len(labels)+1, column=1, sticky='w', pady=12) 