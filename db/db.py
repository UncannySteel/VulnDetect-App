import sqlite3
from typing import List, Dict, Any, Optional
import os
import threading

class SQLiteStore:
    """
    Handles SQLite storage for scan results and application inventory.
    Thread-safe with a lock.
    """
    def __init__(self, db_path: Optional[str] = None):
        # Default DB path: %LOCALAPPDATA%/AppCursor/storage.db
        if db_path is None:
            local_appdata = os.environ.get('LOCALAPPDATA', os.getcwd())
            db_dir = os.path.join(local_appdata, 'AppCursor')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'storage.db')
        self.db_path = db_path
        # Allow connection across threads
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        # Create tables if they don't exist (thread-safe)
        with self.lock:
            cur = self.conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY,
                    scan_type TEXT,
                    scan_timestamp TEXT,
                    status TEXT,
                    details TEXT
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    version TEXT,
                    install_path TEXT,
                    install_date TEXT
                )
            ''')
            self.conn.commit()

    # --- Scan Results Methods ---
    def insert_scan_result(self, scan_type: str, scan_timestamp: str, status: str, details: str):
        # Insert a scan result record (thread-safe)
        with self.lock:
            cur = self.conn.cursor()
            cur.execute('''
                INSERT INTO scan_results (scan_type, scan_timestamp, status, details)
                VALUES (?, ?, ?, ?)
            ''', (scan_type, scan_timestamp, status, details))
            self.conn.commit()

    def fetch_scan_results(self) -> List[Dict[str, Any]]:
        # Fetch all scan results (thread-safe)
        with self.lock:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM scan_results ORDER BY scan_timestamp DESC')
            rows = cur.fetchall()
            return [
                {
                    'id': row[0],
                    'scan_type': row[1],
                    'scan_timestamp': row[2],
                    'status': row[3],
                    'details': row[4],
                } for row in rows
            ]

    def delete_scan_result(self, id: int):
        # Delete a scan result by id (thread-safe)
        with self.lock:
            cur = self.conn.cursor()
            cur.execute('DELETE FROM scan_results WHERE id = ?', (id,))
            self.conn.commit()

    def update_scan_result(self, id: int, **fields):
        # Update scan result fields by id (thread-safe)
        if not fields:
            return
        with self.lock:
            cur = self.conn.cursor()
            columns = ', '.join([f"{k} = ?" for k in fields.keys()])
            values = list(fields.values())
            values.append(id)
            cur.execute(f'UPDATE scan_results SET {columns} WHERE id = ?', values)
            self.conn.commit()

    # --- Application Inventory Methods ---
    def insert_application(self, name: str, version: str, install_path: str, install_date: str):
        # Insert an application record (thread-safe)
        with self.lock:
            cur = self.conn.cursor()
            cur.execute('''
                INSERT INTO applications (name, version, install_path, install_date)
                VALUES (?, ?, ?, ?)
            ''', (name, version, install_path, install_date))
            self.conn.commit()

    def fetch_applications(self) -> List[Dict[str, Any]]:
        # Fetch all applications (thread-safe)
        with self.lock:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM applications ORDER BY name ASC')
            rows = cur.fetchall()
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'version': row[2],
                    'install_path': row[3],
                    'install_date': row[4],
                } for row in rows
            ]

    def delete_application(self, id: int):
        # Delete an application by id (thread-safe)
        with self.lock:
            cur = self.conn.cursor()
            cur.execute('DELETE FROM applications WHERE id = ?', (id,))
            self.conn.commit()

    def update_application(self, id: int, **fields):
        # Update application fields by id (thread-safe)
        if not fields:
            return
        with self.lock:
            cur = self.conn.cursor()
            columns = ', '.join([f"{k} = ?" for k in fields.keys()])
            values = list(fields.values())
            values.append(id)
            cur.execute(f'UPDATE applications SET {columns} WHERE id = ?', values)
            self.conn.commit()

    def close(self):
        # Close the database connection (thread-safe)
        with self.lock:
            self.conn.close()

# Test block for standalone run/demo
'''
if __name__ == "__main__":
    store = SQLiteStore()
    store.insert_scan_result('system', '2024-05-01 12:00:00', 'success', '{"os": "Windows"}')
    store.insert_application('TestApp', '1.0', 'C:/Test', '2024-05-01')
    print("Scan Results:", store.fetch_scan_results())
    print("Applications:", store.fetch_applications())
    # Example update and delete
    store.update_scan_result(1, status='failed')
    store.delete_application(1)
    store.close()
''' 