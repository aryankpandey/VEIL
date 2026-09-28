from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

class PermissionInfoBar(QWidget):
    def __init__(self, origin, feature, callback, parent=None):
        super().__init__(parent)
        self.callback = callback
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        self.setStyleSheet("background-color: #444; color: white; border-bottom: 1px solid #222;")
        
        feature_name = str(feature).split('.')[-1]
        lbl = QLabel(f"The site <b>{origin}</b> wants to use your <b>{feature_name}</b>.")
        layout.addWidget(lbl)
        
        layout.addStretch()
        
        allow_btn = QPushButton("Allow Always")
        allow_btn.clicked.connect(lambda: self.respond("allow"))
        
        allow_once_btn = QPushButton("Allow Once")
        allow_once_btn.clicked.connect(lambda: self.respond("allow_once"))
        
        block_btn = QPushButton("Block")
        block_btn.clicked.connect(lambda: self.respond("block"))
        
        layout.addWidget(allow_btn)
        layout.addWidget(allow_once_btn)
        layout.addWidget(block_btn)
        
    def respond(self, decision):
        self.callback(decision)
        self.deleteLater()
