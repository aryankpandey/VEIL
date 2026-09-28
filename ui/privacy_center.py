from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTabWidget, QWidget, QFormLayout, QComboBox)
from PySide6.QtCore import Qt

class PrivacyCenter(QDialog):
    def __init__(self, profile, is_private, tracker_count=0, cookie_count=0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VEIL Privacy Center")
        self.resize(500, 400)
        self.web_profile = profile
        self.is_private_session = is_private
        self.tracker_count = tracker_count
        self.cookie_count = cookie_count
        
        layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Status Tab
        self.status_tab = QWidget()
        self.setup_status_tab()
        self.tabs.addTab(self.status_tab, "Status")
        
        # Controls Tab
        self.controls_tab = QWidget()
        self.setup_controls_tab()
        self.tabs.addTab(self.controls_tab, "Controls")
        
        layout.addWidget(self.tabs)
        
        # Close btn
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def setup_status_tab(self):
        layout = QVBoxLayout(self.status_tab)
        
        title = QLabel("Privacy status")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("────────────────"))
        
        self.trackers_lbl = QLabel(f"Trackers blocked: {self.tracker_count}")
        self.cookies_lbl = QLabel(f"Cookies controlled: {self.cookie_count}")
        self.permissions_granted_lbl = QLabel("Permissions granted: 0")
        self.permissions_denied_lbl = QLabel("Permissions denied: 0")
        
        session_text = "Active" if self.is_private_session else "Inactive"
        self.private_sessions_lbl = QLabel(f"Private sessions: {session_text}")
        
        self.site_data_lbl = QLabel("Site data: 0 MB")
        
        layout.addWidget(self.trackers_lbl)
        layout.addWidget(self.cookies_lbl)
        
        self.manage_cookies_btn = QPushButton("Manage Cookies")
        self.manage_cookies_btn.clicked.connect(self.open_cookie_manager)
        layout.addWidget(self.manage_cookies_btn)
        
        layout.addWidget(self.permissions_granted_lbl)
        layout.addWidget(self.permissions_denied_lbl)
        layout.addWidget(self.private_sessions_lbl)
        layout.addWidget(self.site_data_lbl)
        layout.addStretch()

    def setup_controls_tab(self):
        layout = QFormLayout(self.controls_tab)
        
        # Create combo boxes for permissions (enforced in Phase 12)
        self.js_combo = self.create_permission_combo()
        layout.addRow("JavaScript:", self.js_combo)
        
        self.cookies_combo = self.create_permission_combo()
        layout.addRow("Cookies:", self.cookies_combo)
        
        self.notifications_combo = self.create_permission_combo()
        layout.addRow("Notifications:", self.notifications_combo)
        
        self.camera_combo = self.create_permission_combo()
        layout.addRow("Camera:", self.camera_combo)
        
        self.mic_combo = self.create_permission_combo()
        layout.addRow("Microphone:", self.mic_combo)
        
        self.location_combo = self.create_permission_combo()
        layout.addRow("Location:", self.location_combo)
        
        self.popups_combo = self.create_permission_combo()
        layout.addRow("Popups:", self.popups_combo)
        
        self.downloads_combo = self.create_permission_combo()
        layout.addRow("Automatic Downloads:", self.downloads_combo)
        
    def create_permission_combo(self):
        combo = QComboBox()
        combo.addItems(["Ask", "Allowed", "Blocked"])
        return combo

    def update_tracker_count(self, count):
        self.tracker_count = count
        if hasattr(self, 'trackers_lbl'):
            self.trackers_lbl.setText(f"Trackers blocked: {self.tracker_count}")

    def update_cookie_count(self, count):
        self.cookie_count = count
        if hasattr(self, 'cookies_lbl'):
            self.cookies_lbl.setText(f"Cookies controlled: {self.cookie_count}")

    def update_permission_counts(self, granted, denied):
        if hasattr(self, 'permissions_granted_lbl'):
            self.permissions_granted_lbl.setText(f"Permissions granted: {granted}")
            self.permissions_denied_lbl.setText(f"Permissions denied: {denied}")

    def open_cookie_manager(self):
        from ui.cookie_dialog import CookieDialog
        current_domain = ""
        main_win = self.parent()
        if main_win and hasattr(main_win, 'tabs'):
            current_browser = main_win.tabs.currentWidget()
            if current_browser:
                current_domain = current_browser.url().host()

        self.cookie_dialog = CookieDialog(self.web_profile.cookieStore(), current_domain, self)
        self.cookie_dialog.show()
