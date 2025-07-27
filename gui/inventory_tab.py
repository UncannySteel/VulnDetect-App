import tkinter as tk
from tkinter import ttk
from theme.windows98 import WIN98_COLORS, WIN98_FONT, WIN98_TITLE_FONT, style_win98_treeview
from gui.tooltip import Tooltip  # Add this import

CHECKED = '\u2611'  # ☑
UNCHECKED = '\u2610'  # ☐

class InventoryTab(ttk.Frame):
    """
    Tab for displaying application inventory in a Win98-style table.
    Allows deleting checked apps (affects DB via callback).
    Supports sorting by Name and Install Date.
    """
    def __init__(self, parent, app_data=None, delete_callback=None, theme_controller=None, *args, **kwargs):
        super().__init__(parent, borderwidth=4, relief="solid")
        self.app_data = app_data or []
        self.delete_callback = delete_callback
        self._sort_column = None
        self._sort_reverse = False
        self.checked_ids = set()  # Track checked rows by app id
        self.theme_controller = theme_controller
        self.apply_theme()
        self._build_ui()

    def apply_theme(self):
        if hasattr(self, 'theme_controller') and self.theme_controller:
            self.theme_controller.apply_inventory_tab_theme(self)
        else:
            self['background'] = WIN98_COLORS['bg']
            style = ttk.Style(self)
            style.theme_use('clam')
            style_win98_treeview(style)
            style.configure('TabFrame.TFrame', background=WIN98_COLORS['panel'], borderwidth=2, relief='groove')
            self.heading.configure(fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['panel'], font=WIN98_FONT)
            self.top_btn_frame.configure(bg=WIN98_COLORS['panel'])
            self.table_frame.configure(bg=WIN98_COLORS['panel'])

    def _build_ui(self):
        # Main panel with consistent outer padding
        main_frame = tk.Frame(self, bg=WIN98_COLORS['panel'], borderwidth=2, relief='groove', highlightbackground=WIN98_COLORS['button_border'], highlightthickness=1)
        main_frame.pack(expand=True, fill='both', padx=24, pady=24)
        self.heading = tk.Label(main_frame, text="Application Inventory", font=WIN98_TITLE_FONT, fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['panel'], pady=8)  # Bold, large heading
        self.heading.pack(anchor='w', pady=(0, 12))
        self.top_btn_frame = tk.Frame(main_frame, bg=WIN98_COLORS['panel'], borderwidth=2, relief='groove', highlightbackground=WIN98_COLORS['button_border'], highlightthickness=1)
        self.top_btn_frame.pack(fill='x', pady=(0, 12))  # More space below buttons
        self.del_btn = ttk.Button(
            self.top_btn_frame,
            text="Delete Selected",
            command=self._on_delete,
            style='Win98.TButton'
        )
        self.del_btn.pack(side='right', padx=8, pady=4)
        Tooltip(self.del_btn, text="Delete all checked applications from the inventory.")
        self.table_frame = tk.Frame(main_frame, bg=WIN98_COLORS['panel'], borderwidth=2, relief='groove', highlightbackground=WIN98_COLORS['button_border'], highlightthickness=1)
        self.table_frame.pack(expand=True, fill='both', pady=(0, 8))  # Consistent spacing below table
        self.columns = ('', "NAME", "VERSION", "PATH", "INSTALL DATE")
        self.tree = ttk.Treeview(self.table_frame,
                                columns=self.columns,
                                show='headings',
                                height=15,
                                selectmode='none',
                                style='Win98.Treeview')
        column_widths = {
            '': 32,
            "NAME": 200,
            "VERSION": 120,
            "PATH": 300,
            "INSTALL DATE": 150
        }
        for col in self.columns:
            if col == '':
                self.tree.heading(col, text='')
            else:
                self.tree.heading(col,
                                text=col,
                                command=lambda c=col: self._on_sort(c) if c != '' else None)
            self.tree.column(col,
                           anchor='w',
                           width=column_widths[col])
        self.scrollbar = ttk.Scrollbar(self.table_frame,
                                orient="vertical",
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.pack(side='left', expand=True, fill='both', padx=(0, 8), pady=8)  # Consistent inner spacing
        self.scrollbar.pack(side='right', fill='y', pady=8)
        self.tree.bind('<Button-1>', self._on_checkbox_click)
        self.refresh(self.app_data)

    def refresh(self, app_data):
        self.app_data = app_data
        self._display_data()

    def _display_data(self):
        self.tree.delete(*self.tree.get_children())
        data = self.app_data[:]
        if self._sort_column and self._sort_column in self.columns:
            idx = self.columns.index(self._sort_column)
            key = None
            if self._sort_column == "NAME":
                key = lambda app: app.get('name', '').lower()
            elif self._sort_column == "INSTALL DATE":
                key = lambda app: app.get('install_date', '')
            if key:
                data.sort(key=key, reverse=self._sort_reverse)
        for app in data:
            app_id = str(app.get('id', ''))
            checked = CHECKED if app_id in self.checked_ids else UNCHECKED
            self.tree.insert('', 'end',
                           iid=app_id,
                           values=(checked,
                                   app.get('name', '').upper(),
                                   app.get('version', ''),
                                   app.get('install_path', ''),
                                   app.get('install_date', '').upper()
                           ))
        # Update header sort indicators (skip checkbox column)
        for col in self.columns:
            if col == '':
                continue
            text = col
            if col == self._sort_column:
                text += ' ↓' if self._sort_reverse else ' ↑'
            self.tree.heading(col, text=text)

    def _on_sort(self, col):
        if col == '':
            return
        if self._sort_column == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = col
            self._sort_reverse = False
        self._display_data()

    def _on_checkbox_click(self, event):
        # Detect if click is in the checkbox column and toggle
        region = self.tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        col = self.tree.identify_column(event.x)
        if col != '#1':  # Checkbox column is always #1
            return
        row = self.tree.identify_row(event.y)
        if not row:
            return
        app_id = row
        if app_id in self.checked_ids:
            self.checked_ids.remove(app_id)
        else:
            self.checked_ids.add(app_id)
        self._display_data()

    def _on_delete(self):
        # Show confirmation dialog before deleting to prevent accidental data loss
        selected = list(self.checked_ids)
        if not selected:
            return
        from tkinter import messagebox
        count = len(selected)
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the {count} selected application(s)?",
            icon='warning')
        if not confirm:
            return
        for app_id in selected:
            self.tree.delete(app_id)
            if self.delete_callback:
                self.delete_callback(app_id)
        self.checked_ids.clear() 