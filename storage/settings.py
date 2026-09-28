from storage.database import DatabaseManager

class SettingsManager:
    def __init__(self):
        self.db = DatabaseManager.get_instance()
        
    def get_setting(self, profile_id, key, default=None):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE profile_id = ? AND key = ?", (profile_id, key))
            row = cursor.fetchone()
            return row[0] if row else default
            
    def set_setting(self, profile_id, key, value):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (profile_id, key, value) 
                VALUES (?, ?, ?)
            ''', (profile_id, key, str(value)))
            conn.commit()
