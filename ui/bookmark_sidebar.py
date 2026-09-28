from PySide6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                               QLineEdit, QMenu, QInputDialog, QMessageBox)
from PySide6.QtCore import Qt, Signal
from storage.bookmarks import BookmarkManager

class BookmarkSidebar(QDockWidget):
    open_url_requested = Signal(str)

    def __init__(self, profile_id="default", parent=None):
        super().__init__("Bookmarks", parent)
        self.profile_id = profile_id
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.bookmark_manager = BookmarkManager()
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        # Search
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search bookmarks...")
        self.search_bar.textChanged.connect(self.filter_bookmarks)
        layout.addWidget(self.search_bar)

        # List
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget)

        self.setWidget(container)
        self.all_bookmarks = []
        self.refresh_bookmarks()

    def refresh_bookmarks(self):
        self.list_widget.clear()
        self.all_bookmarks = self.bookmark_manager.get_bookmarks(profile_id=self.profile_id)
        self.filter_bookmarks(self.search_bar.text())

    def filter_bookmarks(self, text):
        self.list_widget.clear()
        text = text.lower()
        for b in self.all_bookmarks:
            if text in b.title.lower() or text in b.url.lower():
                item = QListWidgetItem(f"{b.title}\n{b.url}")
                item.setData(Qt.UserRole, b)
                self.list_widget.addItem(item)

    def on_item_double_clicked(self, item):
        b = item.data(Qt.UserRole)
        self.open_url_requested.emit(b.url)

    def show_context_menu(self, position):
        item = self.list_widget.itemAt(position)
        if not item:
            return
        
        b = item.data(Qt.UserRole)
        menu = QMenu()
        
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.list_widget.mapToGlobal(position))
        
        if action == edit_action:
            new_title, ok = QInputDialog.getText(self, "Edit Bookmark", "Title:", text=b.title)
            if ok and new_title:
                new_url, ok2 = QInputDialog.getText(self, "Edit Bookmark", "URL:", text=b.url)
                if ok2 and new_url:
                    self.bookmark_manager.edit_bookmark(b.id, new_title, new_url, b.folder_id)
                    self.refresh_bookmarks()
        elif action == delete_action:
            reply = QMessageBox.question(self, "Confirm", "Delete bookmark?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.bookmark_manager.remove_bookmark(b.id)
                self.refresh_bookmarks()
