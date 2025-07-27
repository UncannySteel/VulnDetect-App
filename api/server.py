from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import socket
from datetime import datetime

# function creates a FastAPI app 
# All endpoints use given for data and actions

def create_app(service):
    app = FastAPI(title="Vulnerability Scanner API", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def error_response(code, message, details=None, http_status=400):
        return JSONResponse(
            status_code=http_status,
            content={
                "status": "error",
                "error": {
                    "code": code,
                    "message": message,
                    "details": details,
                },
            },
        )

    @app.get("/api/v1/status")
    def get_status():
        try:
            data = service.get_status()
            return {"status": "success", "data": data}
        except Exception as e:
            return error_response("STATUS_FAILED", "Failed to get scanner status", str(e), 500)

    @app.get("/api/v1/system")
    def get_system():
        try:
            sysdata = service.get_system_profile()
            data = {
                "osName": sysdata.get("os_name", "Windows"),
                "osVersion": sysdata.get("os_version", "Unknown"),
                "architecture": sysdata.get("architecture", "Unknown"),
                "kernelVersion": sysdata.get("kernel_version", "Unknown"),
                "hostname": socket.gethostname(),
                "lastBoot": None,  # Not implemented
                "systemComponents": [],
            }
            for k, v in sysdata.get("components", {}).items():
                data["systemComponents"].append({
                    "name": k,
                    "version": v,
                    "type": "service",
                    "description": f"{k} version info",
                })
            return {"status": "success", "data": data}
        except Exception as e:
            return error_response("SYSTEM_FAILED", "Failed to get system profile", str(e), 500)

    @app.get("/api/v1/applications")
    def get_applications():
        try:
            apps = service.fetch_cached_inventory()
            app_list = []
            for idx, app in enumerate(apps):
                app_list.append({
                    "id": f"app-{idx+1:03d}",
                    "name": app.get("name"),
                    "version": app.get("version"),
                    "installPath": app.get("install_path"),
                    "installDate": app.get("install_date"),
                    "publisher": None,
                    "size": None,
                    "lastModified": None,
                    "vulnerabilityCount": 0,
                    "updateAvailable": False,
                    "updateVersion": None,
                })
            data = {
                "totalApplications": len(app_list),
                "lastScanned": datetime.utcnow().isoformat() + "Z",
                "applications": app_list,
            }
            return {"status": "success", "data": data}
        except Exception as e:
            return error_response("APP_LIST_FAILED", "Failed to get application inventory", str(e), 500)

    @app.post("/api/v1/scan")
    def trigger_scan():
        try:
            service.run_scan()
            return {"status": "success", "message": "Scan started"}
        except Exception as e:
            return error_response("SCAN_FAILED", "Failed to start scan", str(e), 500)

    @app.post("/api/v1/delete_app/{app_id}")
    def delete_app(app_id: int):
        try:
            service.db.delete_application(app_id)
            return {"status": "success", "message": f"App {app_id} deleted"}
        except Exception as e:
            return error_response("DELETE_FAILED", "Failed to delete app", str(e), 500)

    @app.post("/api/v1/send_data")
    def send_data():
        try:
            # Here you would implement the actual data transfer logic
            # For now, just return success
            return {"status": "success", "message": "Data sent to remote server (stub)"}
        except Exception as e:
            return error_response("SEND_FAILED", "Failed to send data", str(e), 500)

    @app.get("/api/v1/dashboard")
    def get_dashboard():
        try:
            return {
                "status": "success",
                "data": {
                    "status": service.get_status(),
                    "system_profile": service.get_system_profile(),
                    "applications": service.fetch_cached_inventory(),
                }
            }
        except Exception as e:
            return error_response("DASHBOARD_FAILED", "Failed to get dashboard data", str(e), 500)

    return app 