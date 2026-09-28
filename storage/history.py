from datetime import datetime, timedelta
from storage.database import DatabaseManager
from models.history_entry import HistoryEntry

class HistoryManager:
    def __init__(self):
        self.db = DatabaseManager.get_instance()

    def add_entry(self, url: str, title: str, profile_id: str = "default", is_private: bool = False):
        if is_private:
            return
        # Ignore new tab page
        if url.startswith("file://") and "new_tab.html" in url:
            return

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO history (url, title, visit_time, profile_id) VALUES (?, ?, ?, ?)",
                (url, title, datetime.now(), profile_id)
            )
            conn.commit()

    def get_history(self, search_query="", profile_id="default"):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if search_query:
                cursor.execute(
                    "SELECT id, url, title, visit_time, profile_id FROM history WHERE profile_id = ? AND (url LIKE ? OR title LIKE ?) ORDER BY visit_time DESC",
                    (profile_id, f"%{search_query}%", f"%{search_query}%")
                )
            else:
                cursor.execute(
                    "SELECT id, url, title, visit_time, profile_id FROM history WHERE profile_id = ? ORDER BY visit_time DESC",
                    (profile_id,)
                )
            rows = cursor.fetchall()
            return [HistoryEntry(r[0], r[1], r[2], r[3], r[4]) for r in rows]

    def delete_entry(self, entry_id: int):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history WHERE id = ?", (entry_id,))
            conn.commit()

    def delete_entries(self, entry_ids: list[int]):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("DELETE FROM history WHERE id = ?", [(eid,) for eid in entry_ids])
            conn.commit()

    def clear_history(self, time_range: str, profile_id: str = "default"):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if time_range == "all_time":
                cursor.execute("DELETE FROM history WHERE profile_id = ?", (profile_id,))
            else:
                now = datetime.now()
                if time_range == "last_hour":
                    threshold = now - timedelta(hours=1)
                elif time_range == "today":
                    threshold = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif time_range == "today_yesterday":
                    threshold = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
                elif time_range == "last_7_days":
                    threshold = now - timedelta(days=7)
                else:
                    threshold = now
                
                cursor.execute("DELETE FROM history WHERE profile_id = ? AND visit_time >= ?", (profile_id, threshold))
            conn.commit()
