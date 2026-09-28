from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                               QComboBox, QMessageBox, QAbstractItemView)
from PySide6.QtCore import Qt
from storage.history import HistoryManager

class HistoryWindow(QWidget):
    def __init__(self, profile_id="default", parent=None):
        super().__init__(parent)
        self.profile_id = profile_id
        self.setWindowTitle("History - VEIL")
        self.resize(800, 600)
        self.history_manager = HistoryManager()

        layout = QVBoxLayout(self)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search history...")
        self.search_bar.textChanged.connect(self.load_history)
        toolbar_layout.addWidget(self.search_bar)

        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected)
        toolbar_layout.addWidget(self.delete_selected_btn)

        self.clear_range_combo = QComboBox()
        self.clear_range_combo.addItems([
            "Last hour", "Today", "Today and yesterday", "Last 7 days", "All time"
        ])
        toolbar_layout.addWidget(self.clear_range_combo)

        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)
        toolbar_layout.addWidget(self.clear_history_btn)

        layout.addLayout(toolbar_layout)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Title", "URL"])
        self.table.setColumnHidden(0, True) # Hide ID
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        self.load_history()

    def load_history(self):
        query = self.search_bar.text()
        entries = self.history_manager.get_history(search_query=query, profile_id=self.profile_id)
        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            id_item = QTableWidgetItem(str(entry.id))
            date_item = QTableWidgetItem(entry.visit_time.strftime("%Y-%m-%d %H:%M:%S"))
            title_item = QTableWidgetItem(entry.title)
            url_item = QTableWidgetItem(entry.url)
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, date_item)
            self.table.setItem(row, 2, title_item)
            self.table.setItem(row, 3, url_item)

    def delete_selected(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            return
        
        ids_to_delete = []
        for row in selected_rows:
            id_str = self.table.item(row, 0).text()
            ids_to_delete.append(int(id_str))
            
        self.history_manager.delete_entries(ids_to_delete)
        self.load_history()

    def clear_history(self):
        range_text = self.clear_range_combo.currentText()
        range_map = {
            "Last hour": "last_hour",
            "Today": "today",
            "Today and yesterday": "today_yesterday",
            "Last 7 days": "last_7_days",
            "All time": "all_time"
        }
        
        reply = QMessageBox.question(self, 'Confirm Clear', 
                                     f'Are you sure you want to clear history for: {range_text}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.history_manager.clear_history(range_map[range_text], profile_id=self.profile_id)
            self.load_history()
