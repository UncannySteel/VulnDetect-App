import socket
from datetime import datetime
import json

# Export scan data (system profile + inventory) in required format

def export_json_data(service, file_path):
    """Export system profile and application inventory as JSON to the given file path."""
    # --- Build system profile in required format ---
    raw_profile = service.get_system_profile()
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
    apps = service.get_app_inventory()
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
    # --- Write JSON to file ---
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    # --- Return the data for optional further use ---
    return data

# Small test block
if __name__ == "__main__":
    from core.service import AppService
    service = AppService()
    export_json_data(service, "test_export.json") 