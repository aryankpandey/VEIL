from PySide6.QtWidgets import QToolBar, QLineEdit, QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal

class BrowserToolBar(QToolBar):
    url_changed = Signal(str)
    back_requested = Signal()
    forward_requested = Signal()
    reload_requested = Signal()
    stop_requested = Signal()
    home_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)

        self.back_action = QAction("←", self)
        self.back_action.triggered.connect(self.back_requested.emit)
        self.addAction(self.back_action)

        self.forward_action = QAction("→", self)
        self.forward_action.triggered.connect(self.forward_requested.emit)
        self.addAction(self.forward_action)

        self.reload_action = QAction("⟳", self)
        self.reload_action.triggered.connect(self.reload_requested.emit)
        self.addAction(self.reload_action)

        self.stop_action = QAction("×", self)
        self.stop_action.triggered.connect(self.stop_requested.emit)
        self.addAction(self.stop_action)

        self.home_action = QAction("🏠", self)
        self.home_action.triggered.connect(self.home_requested.emit)
        self.addAction(self.home_action)

        from PySide6.QtWidgets import QToolButton
        self.privacy_btn = QToolButton(self)
        self.privacy_btn.setText("🛡️")
        self.addWidget(self.privacy_btn)
        
        self.download_btn = QToolButton(self)
        self.download_btn.setText("⬇️")
        self.addWidget(self.download_btn)
        
        self.settings_btn = QToolButton(self)
        self.settings_btn.setText("⚙️")
        self.addWidget(self.settings_btn)

        self.profile_btn = QToolButton(self)
        self.profile_btn.setText("👤")
        self.profile_btn.setPopupMode(QToolButton.InstantPopup)
        self.addWidget(self.profile_btn)

        self.security_btn = QToolButton(self)
        self.security_btn.setText("🌐")
        self.security_btn.setToolTip("View site information")
        self.security_btn.setStyleSheet("border: none; font-size: 16px;")
        self.security_btn.clicked.connect(self.show_security_info)
        self.addWidget(self.security_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self._on_return_pressed)
        self.addWidget(self.url_bar)

    def _on_return_pressed(self):
        self.url_changed.emit(self.url_bar.text())

    def update_url(self, url):
        self.url_bar.setText(url)
        if url.startswith("https://"):
            self.security_btn.setText("🔒")
            self.security_btn.setStyleSheet("color: #4CAF50; border: none; font-size: 16px; padding: 2px;")
        elif url.startswith("http://"):
            self.security_btn.setText("⚠️")
            self.security_btn.setStyleSheet("color: #F44336; border: none; font-size: 16px; padding: 2px;")
        elif url.startswith("file://") or url.startswith("veil://"):
            self.security_btn.setText("📄")
            self.security_btn.setStyleSheet("color: #9E9E9E; border: none; font-size: 16px; padding: 2px;")
        else:
            self.security_btn.setText("🌐")
            self.security_btn.setStyleSheet("color: #9E9E9E; border: none; font-size: 16px; padding: 2px;")

    def show_security_info(self):
        url = self.url_bar.text()
        if not url:
            return
            
        msg = QMessageBox(self)
        msg.setWindowTitle("Site Security")
        if url.startswith("https://"):
            msg.setText("🔒 Connection is secure")
            msg.setInformativeText("Your information (for example, passwords or credit card numbers) is private when it is sent to this site.")
            msg.setIcon(QMessageBox.Information)
        elif url.startswith("http://"):
            msg.setText("⚠️ Connection is not secure")
            msg.setInformativeText("You should not enter any sensitive information on this site (for example, passwords or credit cards), because it could be stolen by attackers.")
            msg.setIcon(QMessageBox.Warning)
        elif url.startswith("file://") or url.startswith("veil://"):
            msg.setText("📄 Local Page")
            msg.setInformativeText("This page is running securely on your local device.")
            msg.setIcon(QMessageBox.Information)
        else:
            msg.setText("🌐 Unknown Protocol")
            msg.setInformativeText("Security status cannot be determined.")
            msg.setIcon(QMessageBox.Question)
        msg.exec()
