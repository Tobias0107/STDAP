from package_name.gui.app import MainWindow
from PyQt6.QtWidgets import QApplication
import sys

class TestfGui:
    def test_gui(self):
        app = QApplication([])
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

