"""
    Examples of how to use the Gui/dashboard for the simulator.
"""
###############################################################################
############################## Manual method ##################################
###############################################################################

# Import dashboard function
from STDAP.gui.dashboard import show_dashboard

# Run dashboard function
show_dashboard()

###############################################################################
############################## Manual method ##################################
###############################################################################

# Import MainWindow used by the dashboard
from STDAP.gui.app import MainWindow

# Additional imports
from PyQt6.QtWidgets import QApplication
import sys

def show_dashboard_manual():
    """
        Manually show dashboard gui by importing the MainWindow and running it with PyQt6.
    """
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


