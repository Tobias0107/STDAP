
from package_name.core.main_class import simulator
from package_name.config.settings import get_settings
from package_name.gui._widgets import SettingsWidget

import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox
)

class MainWindow(QMainWindow):
    def __init__(self):
        # Set basic parameters
        super().__init__()
        self.setWindowTitle("Pedestrianization simulator GUI")
        self.setMinimumSize(QSize(400, 300))

        #######################################################################
        ##################### Basic layout ####################################
        #######################################################################

        # Paged structure
        basic_layout = QVBoxLayout()
        self.pages = QStackedLayout()
        basic_layout.addLayout(self.pages)


        # Previous, Next
        prv_nxt = QHBoxLayout()
        prev = QPushButton("Previous")
        nxt = QPushButton("Next")
        prev.clicked.connect(self.prev_clicked)
        nxt.clicked.connect(self.nxt_clicked)
        prv_nxt.addWidget(prev)
        prv_nxt.addWidget(nxt)
        basic_layout.addLayout(prv_nxt)


        #######################################################################
        ##################### Page 1 ##########################################
        #######################################################################

        # Start with a vertical layout as base.
        page1 = QVBoxLayout()

        # Title
        title = QLabel("Load datasets")
        font = title.font()
        font.setPointSize(30)
        title.setFont(font)
        page1.addWidget(title)

        # KWB path
        page1.addWidget(QLabel("Kerncijfers wijken en buurten Dataset:"))
        kwb_input = QLineEdit()
        kwb_input.setPlaceholderText("Enter full or relative path")
        kwb_input.textChanged.connect(self.kwb_path_set)
        page1.addWidget(kwb_input)

        # Geopackage path
        page1.addWidget(QLabel("Kerncijfers wijken en buurten Dataset:"))
        geopackage_input = QLineEdit()
        geopackage_input.setPlaceholderText("Enter full or relative path")
        geopackage_input.textChanged.connect(self.geopackage_path_set)
        page1.addWidget(geopackage_input)

        # Simulation method dropdown
        sim_box = QComboBox()
        sim_box.addItems(["Pedestrianize a single fraction", "Pedestrianize a range of fractions"])
        sim_box.currentIndexChanged.connect(self.select_simulation)
        page1.addWidget(QLabel("The simulation to perform:"))
        page1.addWidget(sim_box)

        # Finalize
        widget_p1 = QWidget()
        widget_p1.setLayout(page1)
        self.setCentralWidget(widget_p1)
        self.pages.addWidget(widget_p1)

        #######################################################################
        ##################### Page 2 ##########################################
        #######################################################################



        #######################################################################
        ##################### Page 3 ##########################################
        #######################################################################

        settings = get_settings()
        config = SettingsWidget(settings)
        self.pages.addWidget(config)

        #######################################################################
        ##################### Widget creation #################################
        #######################################################################

        widget = QWidget()
        widget.setLayout(basic_layout)
        self.setCentralWidget(widget)

        #######################################################################
        ##################### Methods #########################################
        #######################################################################

    def prev_clicked(self):
        "Decrement page index by 1 (safe)"
        index = self.pages.currentIndex()
        if index > 0:
            self.pages.setCurrentIndex(index - 1)

    def nxt_clicked(self):
        "Increment page index by 1 (safe)"
        index = self.pages.currentIndex()
        if index < 2:
            self.pages.setCurrentIndex(index + 1)

    def kwb_path_set(self, path):
        "Set self.kwb_path to given tekst"
        self.kwb_path = path

    def geopackage_path_set(self, path):
        "Set self.geopackage_path to given tekst"
        self.geopackage_path = path

    def select_simulation(self, index):
        self.simulation = index





