import sys
from PySide6.QtWidgets import QApplication
from app.application import VeilApplication

def main():
    app = QApplication(sys.argv)
    veil_app = VeilApplication()
    veil_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
