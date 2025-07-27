import tkinter as tk
from tkinter import ttk
from gui.inventory_tab import InventoryTab
from gui.status_tab import StatusTab
from core.service import AppService
import threading
from tkinter import messagebox
import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from theme.windows98 import WIN98_COLORS, WIN98_FONT, WIN98_TITLE_FONT, apply_windows98_theme
from remote_comm import RemoteComm
from gui.config_tab import ConfigTab
from gui.system_profile_tab import SystemProfileTab
from gui.tooltip import Tooltip  # Add this import

# (Legacy ConfigPanel and config.save_config comments removed)

class ThemeController:
    def __init__(self, main_app):
        self.main_app = main_app
        self.current_theme = 'windows98'
    def apply_theme(self, theme=None):
        self.current_theme = 'windows98'
        style = ttk.Style(self.main_app)
        apply_windows98_theme(style)
        self.main_app.configure(bg=WIN98_COLORS['bg'])
    def apply_status_tab_theme(self, tab):
        self.apply_theme(self.current_theme)
    def apply_inventory_tab_theme(self, tab):
        self.apply_theme(self.current_theme)
    def apply_system_profile_tab_theme(self, tab):
        self.apply_theme(self.current_theme)
    def apply_config_tab_theme(self, tab):
        self.apply_theme(self.current_theme)

class MainApp(tk.Tk):
    """
    Main window: dark, colorful, resizable, with app name header and tabbed layout.
    Uses AppService to fetch real data for all panels.
    Starts the API server automatically on launch.
    """
    def __init__(self):
        super().__init__()
        self.title("VulnScan Desktop")
        # Set a taller, less wide default window size
        self.geometry("750x600")
        self.minsize(600, 400)
        self.configure(bg="#181a20")
        # Instantiate the service layer first
        self.service = AppService()
        self._current_theme = self.service.get_config().theme
        self.theme_controller = ThemeController(self)
        self.theme_controller.apply_theme(self._current_theme)
        self.service.start_api()  # Start API server automatically
        self._build_ui()

    def _setup_style(self, theme=None):
        # Deprecated: now handled by ThemeController
        pass

    def _build_ui(self):
        # App name header with Scan, Share, Export, and About buttons (Win98-inspired style)
        header_frame = tk.Frame(self, bg=WIN98_COLORS['bg'])
        header_frame.pack(side="top", fill="x", padx=24, pady=(24, 0))  # Consistent outer padding
        header = tk.Label(header_frame, text="VulnScan Desktop", font=WIN98_TITLE_FONT, fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['bg'], pady=8)
        header.pack(side="left", padx=(10, 0))
        # Group action buttons with consistent spacing
        scan_btn = ttk.Button(header_frame, text="Scan", style='Win98.TButton', command=self._on_scan)
        scan_btn.pack(side="right", padx=8, pady=8)
        Tooltip(scan_btn, text="Start a vulnerability scan of your system.")
        share_btn = ttk.Button(header_frame, text="Share with Website", style='Win98.TButton', command=self._on_share_with_website)
        share_btn.pack(side="right", padx=8, pady=8)
        Tooltip(share_btn, text="Send scan results to your configured website.")
        export_btn = ttk.Button(header_frame, text="Export JSON", style='Win98.TButton', command=self._on_export_json)
        export_btn.pack(side="right", padx=8, pady=8)
        Tooltip(export_btn, text="Export scan data as JSON file.")
        about_btn = ttk.Button(header_frame, text="About", style='Win98.TButton', command=self._show_about)
        about_btn.pack(side="right", padx=8, pady=8)
        Tooltip(about_btn, text="Show information about this app.")
        # Tabbed notebook (Win98 style)
        notebook = ttk.Notebook(self, style='Win98.TNotebook')
        notebook.pack(expand=True, fill="both", padx=24, pady=24)  # Consistent outer padding
        # Status tab (real data)
        self.status_tab = StatusTab(notebook, theme_controller=self.theme_controller)
        status = self.service.get_status()
        self.status_tab.update_status(
            state=status.get("state"),
            last_scan=status.get("last_scan"),
            progress=status.get("progress"),
            version=status.get("version"),
            db_freshness=status.get("db_freshness")
        )
        notebook.add(self.status_tab, text="Status")
        profile_data = self.service.get_system_profile()
        self.profile_tab = SystemProfileTab(notebook, profile_data=profile_data, theme_controller=self.theme_controller)
        notebook.add(self.profile_tab, text="System Profile")
        # Inventory tab (real data from DB, with delete support)
        self.inventory_tab = InventoryTab(
            notebook,
            app_data=self.service.fetch_cached_inventory(),
            delete_callback=self._delete_app_from_db,
            theme_controller=self.theme_controller
        )
        notebook.add(self.inventory_tab, text="Application Inventory")
        # Config tab (real, with website URL entry)
        self.config_tab = ConfigTab(notebook, self.service, on_theme_change=self._on_theme_change, theme_controller=self.theme_controller)
        notebook.add(self.config_tab, text="Configuration")
        # Status bar at the bottom for feedback
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            anchor='w',
            font=WIN98_FONT,
            bg=WIN98_COLORS['bg'],
            fg=WIN98_COLORS['accent'],
            relief='sunken',
            bd=1,
            padx=12,
            pady=4
        )
        status_bar.pack(side='bottom', fill='x', padx=0, pady=(0, 8))  # Always visible, clear contrast

    def _build_config_tab(self, parent):
        # This method is now unused (config tab is a placeholder)
        pass

    def _on_scan(self):
        self._set_status("Scanning in progress...")
        trigger_manual_scan(self.service, self.status_tab, self.inventory_tab)

    def _on_share_with_website(self):
        import socket
        from datetime import datetime
        config = self.service.get_config()
        url = (getattr(config, 'remote_url', '') or '').strip()
        # Allow both HTTP and HTTPS URLs
        if not url or not (url.lower().startswith('http://') or url.lower().startswith('https://')):
            self._set_status("No valid HTTP or HTTPS endpoint set. Please set it in Configuration tab.")
            messagebox.showerror("No Endpoint", "Please set a valid HTTP or HTTPS Website URL in the Configuration tab.")
            return
        remote_comm = RemoteComm(url)
        # --- Build system profile in required format ---
        raw_profile = self.service.get_system_profile()
        components = []
        for name, version in raw_profile.get('components', {}).items():
            components.append({
                "name": name,
                "version": version,
                "type": "service",
                "description": f"{name} version info"
            })
        system_profile = {
            "osName": raw_profile.get("os_name"),
            "osVersion": raw_profile.get("os_version"),
            "architecture": raw_profile.get("architecture"),
            "kernelVersion": raw_profile.get("kernel_version"),
            "hostname": socket.gethostname(),
            "lastBoot": None,  # Not implemented
            "systemComponents": components
        }
        # --- Build application inventory in required format ---
        apps = self.service.get_app_inventory()
        app_list = []
        for idx, app in enumerate(apps):
            app_list.append({
                "id": f"app_{idx+1:03d}",
                "name": app.get("name"),
                "version": app.get("version"),
                "installPath": app.get("install_path"),
                "installDate": app.get("install_date"),
                "publisher": app.get("publisher", None),
                "lastModified": app.get("last_modified", None),
                "vulnerabilityCount": app.get("vulnerability_count", 0),
                "updateAvailable": app.get("update_available", False),
                "updateVersion": app.get("update_version", None)
            })
        inventory = {
            "totalApplications": len(app_list),
            "lastScanned": datetime.utcnow().isoformat() + "Z",
            "applications": app_list
        }
        # --- Wrap both in the required top-level format ---
        data = {
            "status": "success",
            "data": {
                "systemProfile": system_profile,
                "applicationInventory": inventory
            }
        }
        # --- Send data in a background thread ---
        def send_task():
            result = remote_comm.send_json(data)
            if result['success']:
                msg = f"Success! Status code: {result['status_code']}"
                self._set_status(msg)
                messagebox.showinfo("Share with Website", msg)
            else:
                msg = f"Error: {result['error']}"
                self._set_status(msg)
                messagebox.showerror("Share with Website", msg)
        threading.Thread(target=send_task, daemon=True).start()

    def _delete_app_from_db(self, app_id):
        # Delete the app from the DB for the current session and refresh the table
        try:
            self.service.db.delete_application(int(app_id))
        except Exception:
            pass
        self.inventory_tab.refresh(self.service.fetch_cached_inventory())

    def on_close(self):
        # Clean up service/db on close
        self.service.close()
        self.destroy()

    def _set_status(self, msg):
        self.status_var.set(msg)

    def _show_about(self):
        # Custom About dialog styled for Windows 98 look
        about_win = tk.Toplevel(self)
        about_win.title("About VulnScan Desktop")
        about_win.configure(bg=WIN98_COLORS['panel'])
        about_win.resizable(False, False)
        about_win.grab_set()
        # Center the dialog
        about_win.update_idletasks()
        w, h = 380, 240
        x = self.winfo_rootx() + (self.winfo_width() - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        about_win.geometry(f"{w}x{h}+{x}+{y}")
        # Main frame
        frame = tk.Frame(about_win, bg=WIN98_COLORS['panel'], borderwidth=2, relief='groove', highlightbackground=WIN98_COLORS['button_border'], highlightthickness=1)
        frame.pack(expand=True, fill='both', padx=24, pady=24)
        # App name
        name_lbl = tk.Label(frame, text="VulnScan Desktop", font=WIN98_TITLE_FONT, fg=WIN98_COLORS['accent'], bg=WIN98_COLORS['panel'])
        name_lbl.pack(anchor='w', pady=(0, 8))
        # Version
        version_lbl = tk.Label(frame, text="Version 1.2.3", font=WIN98_FONT, fg=WIN98_COLORS['text'], bg=WIN98_COLORS['panel'])
        version_lbl.pack(anchor='w', pady=(0, 12))
        # Credits
        credits = (
            "A retro-inspired vulnerability scanner for Windows.\n\n"
            "Developed by Aniraj & AI Assistant\n"
            "Inspired by Windows 98 UI\n\n"
            "© 2024 All rights reserved."
        )
        credits_lbl = tk.Label(frame, text=credits, font=WIN98_FONT, fg=WIN98_COLORS['text'], bg=WIN98_COLORS['panel'], justify='left')
        credits_lbl.pack(anchor='w', pady=(0, 12))
        # Close button
        close_btn = ttk.Button(frame, text="Close", command=about_win.destroy, style='Win98.TButton')
        close_btn.pack(anchor='e', pady=(8, 0))

    def _on_theme_change(self, theme):
        self._current_theme = theme
        self.theme_controller.apply_theme(theme)
        # self.status_tab.apply_theme()  # No longer needed after StatusTab rewrite
        self.inventory_tab.apply_theme()
        self.config_tab.apply_theme()

    def _on_export_json(self):
        from tkinter import filedialog
        from core.export_json import export_json_data
        # Ask user for file destination and export using the shared module
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export JSON Data"
        )
        if file_path:
            try:
                export_json_data(self.service, file_path)
                self._set_status(f"Exported JSON to {file_path}")
            except Exception as e:
                self._set_status(f"Export failed: {e}")

# Function to trigger a scan in the background and update panels
# Scheduling/trigger logic: Only runs when user clicks Scan; uses a thread to keep GUI responsive.
def trigger_manual_scan(service, status_tab, inventory_tab):
    def scan_task():
        service.update_status(state="scanning", progress=0)
        status_tab.update_status(state="scanning", progress=0)
        service.run_scan()
        status = service.get_status()
        status_tab.update_status(
            state=status.get("state"),
            last_scan=status.get("last_scan"),
            progress=status.get("progress"),
            version=status.get("version"),
            db_freshness=status.get("db_freshness")
        )
        app_data = service.fetch_cached_inventory()
        inventory_tab.refresh(app_data)
    threading.Thread(target=scan_task, daemon=True).start()

if __name__ == "__main__":
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop() 