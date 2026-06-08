"""
    Calls the Gui from Python.
"""

from STDAP.gui.app import MainWindow
from PyQt6.QtWidgets import QApplication
import sys

class TestfGui:
    def test_gui(self):
        app = QApplication([])
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

