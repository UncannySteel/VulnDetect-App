from scanner.system_profile import SystemProfile
from scanner.app_inventory import AppInventory
from db.db import SQLiteStore
from datetime import datetime
import threading
import uvicorn
from api.server import create_app
from config.config import get_config, save_config, Config

class AppService:
    """
    Service layer: integrates scanner, inventory, database, and config.
    Provides a clean API for the GUI and API server.
    Can start/stop the API server in a background thread.
    """
    def __init__(self, db_path=None):
        self.config = get_config()
        # Use config for DB path
        self.db = SQLiteStore(db_path or self.config.db_path)
        self.status = {
            "state": "idle",
            "last_scan": None,
            "progress": 0,
            "version": "1.2.3",
            "db_freshness": "Up-to-date"
        }
        self._api_thread = None

    # --- Config Methods ---
    def get_config(self):
        return self.config

    def update_config(self, **kwargs):
        # Update config values and save
        for k, v in kwargs.items():
            if hasattr(self.config, k):
                setattr(self.config, k, v)
        save_config(self.config)
        # If DB path changed, re-init DB
        if 'db_path' in kwargs:
            self.db.close()
            self.db = SQLiteStore(self.config.db_path)
        # If API port or auto_start_api changed, restart API if needed
        if 'api_port' in kwargs or 'auto_start_api' in kwargs:
            self.restart_api()

    # --- Status Methods ---
    def get_status(self):
        return self.status.copy()

    def update_status(self, **kwargs):
        self.status.update(kwargs)

    # --- System Profile Methods ---
    def get_system_profile(self):
        profile = SystemProfile()
        return profile.collect()

    # --- Application Inventory Methods ---
    def get_app_inventory(self):
        inventory = AppInventory()
        return inventory.collect()

    def cache_app_inventory(self):
        apps = self.get_app_inventory()
        for app in apps:
            self.db.insert_application(
                app.get('name', ''),
                app.get('version', ''),
                app.get('install_path', ''),
                app.get('install_date', '')
            )
        return len(apps)

    def fetch_cached_inventory(self):
        return self.db.fetch_applications()

    # --- Scan Logic (Stub) ---
    def run_scan(self):
        from datetime import datetime
        scan_type = "system"
        scan_timestamp = datetime.now().isoformat()
        try:
            self.update_status(state="scanning", progress=0, last_scan=scan_timestamp)
            self.cache_app_inventory()
            status = "success"
            details = '{"apps": %d}' % len(self.fetch_cached_inventory())
            self.db.insert_scan_result(scan_type, scan_timestamp, status, details)
            self.update_status(state="idle", progress=100)
        except Exception as e:
            status = "failed"
            details = '{"error": "%s"}' % str(e).replace('"', '\"')
            self.db.insert_scan_result(scan_type, scan_timestamp, status, details)
            self.update_status(state="error", progress=0)

    # --- API Server Control ---
    def start_api(self, host=None, port=None):
        """
        Start the FastAPI server in a background thread, sharing this service instance.
        """
        if self._api_thread and self._api_thread.is_alive():
            return  # Already running
        host = host or "127.0.0.1"
        port = port or self.config.api_port
        app = create_app(self)
        def run():
            uvicorn.run(app, host=host, port=port)
        self._api_thread = threading.Thread(target=run, daemon=True)
        self._api_thread.start()

    def restart_api(self):
        # Stopping uvicorn programmatically is non-trivial; for now, just start a new one if needed
        self.start_api()

    def stop_api(self):
        # Not implemented
        pass

    def close(self):
        self.db.close()

# Test block for standalone run/demo
'''
if __name__ == "__main__":
    service = AppService()
    print("Status:", service.get_status())
    print("System Profile:", service.get_system_profile())
    print("App Inventory:", service.get_app_inventory())
    service.run_scan()
    print("Cached Inventory:", service.fetch_cached_inventory())
    service.start_api()
    input("Press Enter to stop...")
    service.close()
''' 