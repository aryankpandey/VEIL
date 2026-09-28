from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QPushButton, QHeaderView, QAbstractItemView, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtNetwork import QNetworkCookie

class CookieDialog(QDialog):
    def __init__(self, cookie_store, current_domain="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cookie Manager - VEIL")
        self.resize(700, 500)
        self.cookie_store = cookie_store
        self.current_domain = current_domain
        self.cookies = []
        self.known_identifiers = set()
        
        layout = QVBoxLayout(self)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_cookies)
        
        self.clear_site_btn = QPushButton(f"Clear Cookies for {self.current_domain}" if self.current_domain else "Clear Site Cookies")
        self.clear_site_btn.clicked.connect(self.clear_site_cookies)
        if not self.current_domain:
            self.clear_site_btn.setEnabled(False)
            
        self.clear_all_btn = QPushButton("Clear All Cookies")
        self.clear_all_btn.clicked.connect(self.clear_all_cookies)
        
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.clear_site_btn)
        btn_layout.addWidget(self.clear_all_btn)
        layout.addLayout(btn_layout)
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Domain", "Name", "Value", "Expiration"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Setup Cookie Store callbacks
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)
        
        self.load_cookies()

    def load_cookies(self):
        self.cookies.clear()
        self.known_identifiers.clear()
        self.table.setRowCount(0)
        self.cookie_store.loadAllCookies()

    def on_cookie_added(self, cookie: QNetworkCookie):
        identifier = f"{cookie.domain()}:{cookie.name().data().decode('utf-8', errors='ignore')}"
        if identifier in self.known_identifiers:
            return
            
        self.known_identifiers.add(identifier)
        self.cookies.append(cookie)
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(cookie.domain()))
        self.table.setItem(row, 1, QTableWidgetItem(cookie.name().data().decode('utf-8', errors='ignore')))
        self.table.setItem(row, 2, QTableWidgetItem(cookie.value().data().decode('utf-8', errors='ignore')))
        
        exp = cookie.expirationDate().toString(Qt.ISODate) if not cookie.isSessionCookie() else "Session"
        self.table.setItem(row, 3, QTableWidgetItem(exp))

    def clear_site_cookies(self):
        if not self.current_domain:
            return
        
        reply = QMessageBox.question(self, "Clear Cookies", f"Clear all cookies for {self.current_domain}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for cookie in self.cookies:
                if self.current_domain in cookie.domain() or cookie.domain() in self.current_domain:
                    self.cookie_store.deleteCookie(cookie)
            self.load_cookies()

    def clear_all_cookies(self):
        reply = QMessageBox.question(self, "Clear Cookies", "Clear ALL cookies?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cookie_store.deleteAllCookies()
            self.load_cookies()
