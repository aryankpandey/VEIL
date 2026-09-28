from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, 
                               QPushButton, QHBoxLayout)
from storage.settings import SettingsManager

class SettingsWindow(QDialog):
    def __init__(self, profile_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - VEIL")
        self.resize(400, 300)
        self.profile_id = profile_id
        self.settings_manager = SettingsManager()
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Dark", "Light"])
        theme_val = self.settings_manager.get_setting(self.profile_id, "theme", "System")
        self.theme_combo.setCurrentText(theme_val)
        form.addRow("Theme:", self.theme_combo)
        
        # Startup Behavior
        self.startup_combo = QComboBox()
        self.startup_combo.addItems(["Open New Tab Page", "Restore Previous Session"])
        startup_val = self.settings_manager.get_setting(self.profile_id, "startup_behavior", "Open New Tab Page")
        self.startup_combo.setCurrentText(startup_val)
        form.addRow("On Startup:", self.startup_combo)
        
        # Default Search Engine
        self.search_combo = QComboBox()
        self.search_combo.addItems(["DuckDuckGo", "Google", "Bing"])
        search_val = self.settings_manager.get_setting(self.profile_id, "search_engine", "DuckDuckGo")
        self.search_combo.setCurrentText(search_val)
        form.addRow("Search Engine:", self.search_combo)
        
        # Download Behavior
        self.download_combo = QComboBox()
        self.download_combo.addItems(["Use Default Path", "Ask where to save each file"])
        download_val = self.settings_manager.get_setting(self.profile_id, "download_behavior", "Use Default Path")
        self.download_combo.setCurrentText(download_val)
        form.addRow("Downloads:", self.download_combo)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

    def save_settings(self):
        self.settings_manager.set_setting(self.profile_id, "theme", self.theme_combo.currentText())
        self.settings_manager.set_setting(self.profile_id, "startup_behavior", self.startup_combo.currentText())
        self.settings_manager.set_setting(self.profile_id, "search_engine", self.search_combo.currentText())
        self.settings_manager.set_setting(self.profile_id, "download_behavior", self.download_combo.currentText())
        self.accept()
