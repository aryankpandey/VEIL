import uuid
from storage.database import DatabaseManager
from models.browser_profile import BrowserProfile
import os

class ProfileManager:
    def __init__(self):
        self.db = DatabaseManager.get_instance()
        self.profiles_dir = os.path.join(self.db.db_dir, "profiles")
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)

    def get_all_profiles(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, is_private FROM profiles")
            return [BrowserProfile(r[0], r[1], bool(r[2])) for r in cursor.fetchall()]

    def create_profile(self, name: str, is_private: bool = False):
        p_id = str(uuid.uuid4())
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO profiles (id, name, is_private) VALUES (?, ?, ?)", (p_id, name, int(is_private)))
            conn.commit()
            return p_id

    def get_profile_data_path(self, profile_id: str):
        path = os.path.join(self.profiles_dir, profile_id)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
