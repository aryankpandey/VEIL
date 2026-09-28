import sqlite3
import os

class DatabaseManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Store in user data dir for VEIL
        self.db_dir = os.path.join(os.path.expanduser("~"), ".veil")
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        self.db_path = os.path.join(self.db_dir, "veil.db")
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    visit_time TIMESTAMP NOT NULL,
                    profile_id TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    is_private BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            cursor.execute("INSERT OR IGNORE INTO profiles (id, name, is_private) VALUES ('default', 'Personal', 0)")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    total_bytes INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    feature TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    profile_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    PRIMARY KEY (profile_id, key)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmark_folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parent_id INTEGER,
                    profile_id TEXT NOT NULL,
                    FOREIGN KEY(parent_id) REFERENCES bookmark_folders(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    folder_id INTEGER,
                    profile_id TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY(folder_id) REFERENCES bookmark_folders(id)
                )
            ''')
            conn.commit()
