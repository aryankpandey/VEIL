from storage.database import DatabaseManager
from dataclasses import dataclass

@dataclass
class DownloadEntry:
    id: int
    profile_id: str
    url: str
    file_name: str
    file_path: str
    total_bytes: int
    timestamp: str

class DownloadManager:
    def __init__(self):
        self.db = DatabaseManager.get_instance()

    def add_download(self, profile_id, url, file_name, file_path, total_bytes):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO downloads (profile_id, url, file_name, file_path, total_bytes)
                VALUES (?, ?, ?, ?, ?)
            ''', (profile_id, url, file_name, file_path, total_bytes))
            conn.commit()
            return cursor.lastrowid

    def get_downloads(self, profile_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, profile_id, url, file_name, file_path, total_bytes, timestamp 
                FROM downloads WHERE profile_id = ? ORDER BY timestamp DESC
            ''', (profile_id,))
            return [DownloadEntry(*r) for r in cursor.fetchall()]

    def clear_downloads(self, profile_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM downloads WHERE profile_id = ?", (profile_id,))
            conn.commit()
