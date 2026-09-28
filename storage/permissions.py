from storage.database import DatabaseManager

class PermissionManager:
    def __init__(self):
        self.db = DatabaseManager.get_instance()

    def set_permission(self, profile_id, origin, feature, status):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM permissions WHERE profile_id = ? AND origin = ? AND feature = ?", 
                           (profile_id, origin, feature))
            cursor.execute("INSERT INTO permissions (profile_id, origin, feature, status) VALUES (?, ?, ?, ?)",
                           (profile_id, origin, feature, status))
            conn.commit()

    def get_permission(self, profile_id, origin, feature):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM permissions WHERE profile_id = ? AND origin = ? AND feature = ?",
                           (profile_id, origin, feature))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_all_permissions(self, profile_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT origin, feature, status FROM permissions WHERE profile_id = ?", (profile_id,))
            return cursor.fetchall()
