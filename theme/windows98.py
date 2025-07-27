# Windows 98 theme constants and helpers for Tkinter GUI
# Updated for classic Win98 palette and style

WIN98_COLORS = {
    'bg': '#C0C0C0',            # Main background (light grey)
    'panel': '#B0B0B0',         # Slightly darker panel for depth
    'accent': '#0000A0',        # Windows 98 blue for headers/titles
    'accent2': '#FFFFFF',       # White for highlights
    'text': '#000000',          # Black text
    'button_bg': '#C0C0C0',     # Button background
    'button_fg': '#000000',     # Button text (black)
    'button_border': '#808080', # Button border (classic grey)
    'button_shadow': '#808080', # Button shadow
    'tab_active': '#B0B0B0',    # Active tab (panel color)
    'tab_inactive': '#C0C0C0',  # Inactive tab (main bg)
    'tree_bg': '#B0B0B0',       # Table background
    'tree_border': '#808080',   # Table border
    'progress_green': '#00C000',# Green for progress bar
    'warning': '#FFA500',       # Orange for warnings (better accessibility)
    'error': '#FF4D4D',         # Red for errors
}

WIN98_FONT = ("MS Sans Serif", 10)  # Standard font
WIN98_TITLE_FONT = ("MS Sans Serif", 13, "bold")  # Bold for headers
WIN98_MONO_FONT = ("Consolas", 9)  # For tables/monospace

from tkinter import ttk

def style_win98_button(style: ttk.Style):
    # Classic Win98 button style
    style.configure('Win98.TButton',
        font=WIN98_FONT,
        foreground=WIN98_COLORS['button_fg'],
        background=WIN98_COLORS['button_bg'],
        borderwidth=2,
        relief='raised',
        padding=6,
    )
    style.map('Win98.TButton',
        background=[('active', WIN98_COLORS['panel'])],
        relief=[('pressed', 'sunken'), ('active', 'raised')],
    )

def style_win98_tabs(style: ttk.Style):
    # Notebook (tabs) style
    style.configure('Win98.TNotebook',
        background=WIN98_COLORS['bg'],
        borderwidth=1,
    )
    style.configure('Win98.TNotebook.Tab',
        font=WIN98_FONT,
        background=WIN98_COLORS['tab_inactive'],
        foreground=WIN98_COLORS['button_fg'],
        padding=[10, 4],
        borderwidth=1,
        relief='raised',
    )
    style.map('Win98.TNotebook.Tab',
        background=[('selected', WIN98_COLORS['tab_active'])],
        foreground=[('selected', WIN98_COLORS['accent'])],
        relief=[('selected', 'sunken'), ('!selected', 'raised')],
    )

def style_win98_treeview(style: ttk.Style):
    # Table style
    style.configure('Win98.Treeview',
        font=WIN98_MONO_FONT,
        background=WIN98_COLORS['tree_bg'],
        foreground=WIN98_COLORS['text'],
        fieldbackground=WIN98_COLORS['tree_bg'],
        bordercolor=WIN98_COLORS['tree_border'],
        borderwidth=1,
        rowheight=22,
    )
    style.map('Win98.Treeview',
        background=[('selected', WIN98_COLORS['accent2'])],
        foreground=[('selected', WIN98_COLORS['accent'])],
    )

def apply_windows98_theme(widget_or_style):
    """
    Apply Windows 98 styles to the given ttk.Style or widget's style.
    Accepts either a ttk.Style instance or a widget (from which a Style will be created).
    """
    if isinstance(widget_or_style, ttk.Style):
        style = widget_or_style
    else:
        style = ttk.Style(widget_or_style)
    style_win98_button(style)
    style_win98_tabs(style)
    style_win98_treeview(style)
    # Green progress bar for Win98 look
    style.configure(
        "Win98.Horizontal.TProgressbar",
        troughcolor=WIN98_COLORS['panel'],
        background=WIN98_COLORS['progress_green'],
        bordercolor=WIN98_COLORS['button_border'],
        lightcolor=WIN98_COLORS['accent2'],
        darkcolor=WIN98_COLORS['accent'],
    )
    # Entry style (simple, flat)
    style.configure('Win98.TEntry',
        font=WIN98_FONT,
        fieldbackground=WIN98_COLORS['bg'],
        foreground=WIN98_COLORS['text'],
        borderwidth=2,
        relief='flat',
    ) 