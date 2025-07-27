import winreg
from typing import List, Dict, Any
from datetime import datetime
import os

class AppInventory:
    """
    Collects installed applications from Windows registry (both 32-bit and 64-bit views).
    Tries multiple fields for install path; install date is only available if present in registry.
    """
    UNINSTALL_PATHS = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    def __init__(self):
        self.apps = []

    def collect(self) -> List[Dict[str, Any]]:
        # Collect installed applications from all relevant registry paths
        seen = set()
        for root, path in self.UNINSTALL_PATHS:
            try:
                with winreg.OpenKey(root, path) as key:
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                name = self._get_reg_value(subkey, 'DisplayName')
                                if not name or name in seen:
                                    continue
                                seen.add(name)
                                version = self._get_reg_value(subkey, 'DisplayVersion')
                                # Try multiple fields for install path
                                install_path = self._get_reg_value(subkey, 'InstallLocation')
                                if not install_path:
                                    uninstall_str = self._get_reg_value(subkey, 'UninstallString')
                                    if uninstall_str:
                                        install_path = os.path.dirname(uninstall_str)
                                if not install_path:
                                    display_icon = self._get_reg_value(subkey, 'DisplayIcon')
                                    if display_icon:
                                        install_path = os.path.dirname(display_icon)
                                # Install date: only available if present in registry
                                install_date = self._get_reg_value(subkey, 'InstallDate')
                                if install_date and len(install_date) == 8 and install_date.isdigit():
                                    try:
                                        install_date = datetime.strptime(install_date, "%Y%m%d").strftime("%Y-%m-%d")
                                    except Exception:
                                        pass
                                self.apps.append({
                                    'name': name,
                                    'version': version or 'Unknown',
                                    'install_path': install_path or 'Unknown',
                                    'install_date': install_date or 'Unknown',
                                })
                        except Exception:
                            continue
            except Exception:
                continue
        return self.apps

    def _get_reg_value(self, key, value):
        # Helper to safely get a registry value
        try:
            return winreg.QueryValueEx(key, value)[0]
        except Exception:
            return None

    def display(self):
        # Print the collected application inventory in a readable format
        if not self.apps:
            self.collect()
        for app in self.apps:
            print(f"{app['name']} | Version: {app['version']} | Path: {app['install_path']} | Installed: {app['install_date']}")

# Test block for standalone run/demo
'''
if __name__ == "__main__":
    inventory = AppInventory()
    inventory.collect()
    inventory.display()
'''