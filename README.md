# VulnDetect-App

A desktop application for Windows that scans for installed applications, collects system profile data, and exposes this information via a GUI and REST API. Designed with a retro Windows 98 theme for a nostalgic look.

---

## Features
- **GUI**: Tabbed interface for status, system profile, app inventory, and configuration.
- **Vulnerability Scan**: Scans installed applications from the Windows registry.
- **System Profile**: Collects OS, kernel, and key component versions.
- **REST API**: FastAPI server exposes scan results and inventory.
- **Export/Share**: Export scan data as JSON or send to a remote HTTPS endpoint.
- **Theming**: Custom Windows 98-inspired theme.
- **SQLite Storage**: Persists scan results and inventory.

---

## Project Structure
```text
main.py                # Entry point: launches GUI and API
requirements.txt       # Python dependencies
remote_comm.py         # Handles secure remote data sharing

/api/                  # FastAPI server and endpoints
/core/                 # Service layer and JSON export
/db/                   # SQLite database logic
/gui/                  # Tkinter GUI components
/scanner/              # System and app inventory collectors
/config/               # Config file management
/theme/                # Windows 98 theme for GUI
```

---

## Setup
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the app**
   ```bash
   python main.py
   ```

---

## Usage
- **Scan**: Click 'Scan' in the GUI to inventory installed apps.
- **Export**: Use 'Export JSON' to save scan results.
- **Share**: Configure a remote HTTPS URL and use 'Share with Website'.
- **API**: Access endpoints (default: `http://localhost:7869/api/v1/`):
  - `/status` — App status
  - `/system` — System profile
  - `/applications` — Installed apps
  - `/scan` — Trigger scan

---

## Configuration
- Config file stored at `%LOCALAPPDATA%/AppCursor/config.json`.
- Options: API port, DB path, theme, auto-start API, remote URL.

---

## Dependencies
- `requests` — HTTP requests
- `fastapi` — REST API
- `uvicorn` — ASGI server
- Standard library: `tkinter`, `sqlite3`, `platform`, `winreg`, etc.

---

## Notes
- Windows-only (uses registry and PowerShell).
- All data is local unless explicitly shared.
- For retro look, see `/theme/windows98.py`.

---