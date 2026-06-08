"""
    This file contains the show_dashboard function to show the Simulation dashboard.
"""

from STDAP.gui.app import MainWindow
from PyQt6.QtWidgets import QApplication
import sys

def show_dashboard():
    """
        This function creates and shows a dashboard for running simulations on
        the effect of pedestrianization on transit distance.

        Command line arguments are given to the QApplication.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
