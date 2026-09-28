from PySide6.QtWidgets import QTabWidget, QToolButton
from PySide6.QtCore import Signal

class BrowserTabBar(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

        # Add new tab button
        self.add_button = QToolButton(self)
        self.add_button.setText("+")
        self.add_button.clicked.connect(self.request_new_tab)
        self.setCornerWidget(self.add_button)

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)
            
    def request_new_tab(self):
        # We need to tell the parent window to add a new tab
        if hasattr(self.parent(), 'add_new_tab'):
            self.parent().add_new_tab()
