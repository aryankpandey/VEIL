from datetime import datetime
from storage.database import DatabaseManager
from models.bookmark import Bookmark, BookmarkFolder

class BookmarkManager:
    def __init__(self):
        self.db = DatabaseManager.get_instance()

    def add_bookmark(self, title: str, url: str, folder_id: int = None, profile_id: str = "default"):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bookmarks (title, url, folder_id, profile_id, created_at) VALUES (?, ?, ?, ?, ?)",
                (title, url, folder_id, profile_id, datetime.now())
            )
            conn.commit()
            return cursor.lastrowid

    def edit_bookmark(self, b_id: int, title: str, url: str, folder_id: int = None):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE bookmarks SET title = ?, url = ?, folder_id = ? WHERE id = ?",
                (title, url, folder_id, b_id)
            )
            conn.commit()

    def remove_bookmark(self, b_id: int):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookmarks WHERE id = ?", (b_id,))
            conn.commit()

    def get_bookmarks(self, profile_id: str = "default"):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, url, folder_id, profile_id, created_at FROM bookmarks WHERE profile_id = ? ORDER BY created_at DESC",
                (profile_id,)
            )
            rows = cursor.fetchall()
            return [Bookmark(*r) for r in rows]

    def add_folder(self, name: str, parent_id: int = None, profile_id: str = "default"):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bookmark_folders (name, parent_id, profile_id) VALUES (?, ?, ?)",
                (name, parent_id, profile_id)
            )
            conn.commit()
            return cursor.lastrowid
            
    def get_folders(self, profile_id: str = "default"):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, parent_id, profile_id FROM bookmark_folders WHERE profile_id = ?",
                (profile_id,)
            )
            rows = cursor.fetchall()
            return [BookmarkFolder(*r) for r in rows]
