from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QProgressBar, QFrame)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from storage.downloads import DownloadManager
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
import os

class DownloadItemWidget(QFrame):
    def __init__(self, download_request: QWebEngineDownloadRequest = None, entry=None, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.download_request = download_request
        self.entry = entry
        
        layout = QVBoxLayout(self)
        
        top_layout = QHBoxLayout()
        name = self.entry.file_name if self.entry else self.download_request.downloadFileName()
        self.name_lbl = QLabel(f"<b>{name}</b>")
        top_layout.addWidget(self.name_lbl)
        top_layout.addStretch()
        
        self.action_btn = QPushButton()
        if self.download_request:
            self.action_btn.setText("Cancel")
            self.action_btn.clicked.connect(self.cancel_download)
        else:
            self.action_btn.setText("Open Folder")
            self.action_btn.clicked.connect(self.open_folder)
        top_layout.addWidget(self.action_btn)
        
        layout.addLayout(top_layout)
        
        if self.download_request:
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 100)
            layout.addWidget(self.progress_bar)
            
            self.download_request.receivedBytesChanged.connect(self.update_progress)
            self.download_request.stateChanged.connect(self.state_changed)
        else:
            size_mb = self.entry.total_bytes / (1024 * 1024) if self.entry.total_bytes else 0
            size_lbl = QLabel(f"{size_mb:.2f} MB - {self.entry.timestamp}")
            layout.addWidget(size_lbl)

    def update_progress(self):
        if self.download_request.totalBytes() > 0:
            val = int(self.download_request.receivedBytes() * 100 / self.download_request.totalBytes())
            self.progress_bar.setValue(val)

    def state_changed(self, state):
        if state == QWebEngineDownloadRequest.DownloadCompleted:
            self.action_btn.setText("Open Folder")
            self.action_btn.clicked.disconnect()
            self.action_btn.clicked.connect(self.open_folder)
        elif state == QWebEngineDownloadRequest.DownloadCancelled or state == QWebEngineDownloadRequest.DownloadInterrupted:
            self.action_btn.setText("Canceled")
            self.action_btn.setEnabled(False)

    def cancel_download(self):
        if self.download_request:
            self.download_request.cancel()

    def open_folder(self):
        path = self.entry.file_path if self.entry else self.download_request.downloadDirectory()
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))

class DownloadWindow(QWidget):
    def __init__(self, profile_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads - VEIL")
        self.resize(500, 600)
        self.profile_id = profile_id
        self.manager = DownloadManager()
        
        layout = QVBoxLayout(self)
        
        # Scroll area for items
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        
        layout.addWidget(self.scroll)
        
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        btn_layout.addStretch()
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
        
        self.load_history()
        
    def load_history(self):
        # Clear layout
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        entries = self.manager.get_downloads(self.profile_id)
        for entry in entries:
            w = DownloadItemWidget(entry=entry)
            self.scroll_layout.addWidget(w)

    def add_active_download(self, download_request):
        w = DownloadItemWidget(download_request=download_request)
        self.scroll_layout.insertWidget(0, w)
        self.show()
        self.raise_()

    def clear_history(self):
        self.manager.clear_downloads(self.profile_id)
        self.load_history()
