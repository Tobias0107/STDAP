"""
    This file contains the MainWindow class with the Simulation dashboard.

    Code was created with help of chat-gpt.
"""

import sys

from PyQt6.QtCore import Qt, QSize, QObject, pyqtSignal, QThread, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QTableWidgetItem,
    QTableWidget,
    QListWidgetItem,
    QScrollArea,
    QToolButton,
    QListView
)

from package_name.core.main_class import simulator
from package_name.gui._widgets import CollapsibleBox


class CollapsibleBox(QWidget):

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        #######################################################################
        # Toggle button
        #######################################################################

        self.toggle_button = QToolButton()
        self.toggle_button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        #######################################################################
        # Content area
        #######################################################################

        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setStyleSheet(
            "QScrollArea { background-color: white; border: none; }"
        )

        self.content_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)

        #######################################################################
        # Animation
        #######################################################################

        self.toggle_animation = QParallelAnimationGroup(self)

        self.content_animation = QPropertyAnimation(
            self.content_area,
            b"maximumHeight"
        )

        self.content_animation.setDuration(200)

        self.toggle_animation.addAnimation(self.content_animation)

        #######################################################################
        # Layout
        #######################################################################

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)

        #######################################################################
        # Signals
        #######################################################################

        self.toggle_button.clicked.connect(self.toggle)

    def toggle(self):

        checked = self.toggle_button.isChecked()

        self.toggle_button.setArrowType(
            Qt.ArrowType.DownArrow
            if checked
            else Qt.ArrowType.RightArrow
        )

        direction = (
            QAbstractAnimation.Direction.Forward
            if checked
            else QAbstractAnimation.Direction.Backward
        )

        self.toggle_animation.setDirection(direction)
        self.toggle_animation.start()

    def setContentLayout(self, content_layout):

        #######################################################################
        # Destroy old layout
        #######################################################################

        old_widget = self.content_area.widget()

        if old_widget is not None:
            old_widget.deleteLater()

        #######################################################################
        # Create content widget
        #######################################################################

        content = QWidget()
        content.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        content.setLayout(content_layout)

        self.content_area.setWidget(content)

        collapsed_height = 0
        content_height = content.sizeHint().height()

        self.content_animation.setStartValue(collapsed_height)
        self.content_animation.setEndValue(content_height)


class SimulationWorker(QObject):

    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, simulator, mode, city, params):
        super().__init__()
        self.simulator = simulator
        self.mode = mode
        self.city = city
        self.params = params

    def run(self):

        try:
            self.log.emit("Starting simulation...")

            self.log.emit(f"Importing city network: {self.city}")

            self.simulator.choose_city(self.city)

            if self.mode == 0:
                self.simulator.Sim_trans_dist_single(
                    **self.params
                )
            else:
                self.simulator.Sim_trans_dist_multiple(
                    **self.params
                )

            self.log.emit("Simulation finished.")

        except Exception as e:
            self.log.emit(f"ERROR: {str(e)}")

        self.finished.emit()

class StreamRedirector:
    def __init__(self, signal):
        self.signal = signal

    def write(self, text):
        if text.strip():
            self.signal.emit(text)

    def flush(self):
        pass


class MainWindow(QMainWindow):

    def __init__(self):
        # Create widget
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(QSize(1200, 800))

        # Start parameters
        self.simulator = None
        self.simulation = 0
        self.kwb_path = ""
        self.geopackage_path = ""

        # Widget containing main_layout
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout = header, subtitle, page_content, navigation, statusbar
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(30, 20, 30, 20)
        self.main_layout.setSpacing(20)

        # Title and subtitle
        header = QLabel("Pedestrianization Simulator")
        header.setObjectName("headerTitle")
        subtitle = QLabel("Simulate the distance to the nearest transit stop after pedestrianizing a percentage of a cities road length.")
        subtitle.setObjectName("headerSubtitle")
        self.main_layout.addWidget(header)
        self.main_layout.addWidget(subtitle)

        # Create pages layout
        self.pages = QStackedWidget()
        self.main_layout.addWidget(self.pages)
        self.page_dataset = self.create_dataset_page()
        self.page_simulation = self.create_simulation_page()
        self.pages.addWidget(self.page_dataset)
        self.pages.addWidget(self.page_simulation)

        # Navigation buttons
        nav = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous")
        self.next_btn = QPushButton("Next →")
        self.prev_btn.clicked.connect(self.prev_clicked)
        self.next_btn.clicked.connect(self.next_clicked)
        nav.addStretch()
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.next_btn)
        self.main_layout.addLayout(nav)

        # Statusbar
        self.statusBar().showMessage("Ready")
        # Stylesheet
        self.setStyleSheet(self.stylesheet())

    def create_dataset_page(self):
        """
        ### Create a widget for the entire page.
        Everything needed to initialize the simulator:\n
        - Path to csv, geopackage
        - Choose simulation
        - Advanced settings
        """

        ###########################################################################
        ##################### Create page #########################################
        ###########################################################################

        page = QWidget()

        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(20)

        ###########################################################################
        ##################### Main dataset card ###################################
        ###########################################################################

        dataset_group = QGroupBox("Dataset loading")

        dataset_layout = QFormLayout()
        dataset_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        dataset_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        dataset_layout.setVerticalSpacing(18)
        dataset_layout.setHorizontalSpacing(20)

        ###########################################################################
        ##################### Simulation mode #####################################
        ###########################################################################

        self.sim_box = QComboBox()
        self.sim_box.setView(QListView())

        self.sim_box.addItems([
            "Pedestrianize a single fraction",
            "Pedestrianize a range of fractions"
        ])

        self.sim_box.currentIndexChanged.connect(
            self.select_simulation
        )

        dataset_layout.addRow(
            "Simulation mode:",
            self.sim_box
        )

        ###########################################################################
        ##################### CSV path ############################################
        ###########################################################################

        self.kwb_input = QLineEdit()

        self.kwb_input.setPlaceholderText(
            "Select CSV dataset"
        )

        kwb_browse = QPushButton("Browse")
        kwb_browse.clicked.connect(self.select_csv)

        kwb_row = QHBoxLayout()
        kwb_row.setContentsMargins(0, 0, 0, 0)

        kwb_row.addWidget(self.kwb_input)
        kwb_row.addWidget(kwb_browse)

        dataset_layout.addRow(
            "CSV dataset:",
            kwb_row
        )

        ###########################################################################
        ##################### Geopackage path #####################################
        ###########################################################################

        self.geo_input = QLineEdit()

        self.geo_input.setPlaceholderText(
            "Select geopackage"
        )

        geo_browse = QPushButton("Browse")
        geo_browse.clicked.connect(
            self.select_geopackage
        )

        geo_row = QHBoxLayout()
        geo_row.setContentsMargins(0, 0, 0, 0)

        geo_row.addWidget(self.geo_input)
        geo_row.addWidget(geo_browse)

        dataset_layout.addRow(
            "Geopackage:",
            geo_row
        )

        ###########################################################################
        ##################### Load simulator ######################################
        ###########################################################################

        load_btn = QPushButton("Load simulator")

        load_btn.setMinimumHeight(42)

        load_btn.clicked.connect(
            self.load_simulator
        )

        dataset_layout.addRow(load_btn)

        ###########################################################################
        ##################### Advanced settings ###################################
        ###########################################################################

        self.settings = get_settings()

        advanced = CollapsibleBox("Advanced settings")

        advanced.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        ###########################################################################
        # Main advanced settings layout
        ###########################################################################

        advanced_layout = QHBoxLayout()
        advanced_layout.setContentsMargins(10, 10, 10, 10)
        advanced_layout.setSpacing(25)

        ###########################################################################
        ##################### Data import settings ################################
        ###########################################################################

        import_group = QGroupBox("Data import settings")

        import_layout = QVBoxLayout()
        import_layout.setSpacing(20)

        ###########################################################################
        # Column mappings
        ###########################################################################

        mapping_label = QLabel(
            "Dataset column mappings"
        )

        mapping_label.setObjectName(
            "settingsSectionTitle"
        )

        import_layout.addWidget(mapping_label)

        self.column_table = QTableWidget()

        self.column_table.setColumnCount(2)

        self.column_table.setHorizontalHeaderLabels([
            "Internal field",
            "Dataset column name"
        ])

        self.column_table.verticalHeader().setVisible(False)

        self.column_table.setRowCount(
            len(self.settings.dataset_column_names)
        )

        for row, (key, value) in enumerate(
            self.settings.dataset_column_names.items()
        ):

            internal_item = QTableWidgetItem(key)

            internal_item.setFlags(
                internal_item.flags() &
                ~Qt.ItemFlag.ItemIsEditable
            )

            self.column_table.setItem(
                row,
                0,
                internal_item
            )

            self.column_table.setItem(
                row,
                1,
                QTableWidgetItem(value)
            )

        self.column_table.horizontalHeader().setStretchLastSection(True)

        self.column_table.setMinimumHeight(500)

        import_layout.addWidget(self.column_table)

        ###########################################################################
        # CSV parsing options
        ###########################################################################

        csv_group = QGroupBox("CSV parsing")

        csv_layout = QFormLayout()

        csv_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        ###########################################################################
        # Delimiter
        ###########################################################################

        self.delim_box = QComboBox()
        self.delim_box.setView(QListView())

        self.delim_box.addItems([
            ",",
            ";",
            "\\t",
            "|"
        ])

        self.delim_box.setCurrentText(
            self.settings.dataset_delim
        )

        csv_layout.addRow(
            "Delimiter:",
            self.delim_box
        )

        ###########################################################################
        # Decimal separator
        ###########################################################################

        self.decimal_box = QComboBox()
        self.decimal_box.setView(QListView())

        self.decimal_box.addItems([
            ".",
            ","
        ])

        self.decimal_box.setCurrentText(
            self.settings.dataset_decimal_separator
        )

        csv_layout.addRow(
            "Decimal separator:",
            self.decimal_box
        )

        ###########################################################################
        # Null strings
        ###########################################################################

        null_layout = QVBoxLayout()

        self.null_list = QListWidget()
        self.null_list.setEditTriggers(
            QListWidget.EditTrigger.DoubleClicked |
            QListWidget.EditTrigger.EditKeyPressed
        )

        for item in self.settings.dataset_nullstring:
            self.null_list.addItem(item)

        null_btn_row = QHBoxLayout()

        add_null = QPushButton("Add")
        remove_null = QPushButton("Remove")

        add_null.clicked.connect(self.add_null_string)
        remove_null.clicked.connect(self.remove_null_string)

        null_btn_row.addWidget(add_null)
        null_btn_row.addWidget(remove_null)

        null_layout.addWidget(self.null_list)
        null_layout.addLayout(null_btn_row)

        csv_layout.addRow(
            "NULL strings:",
            null_layout
        )

        csv_group.setLayout(csv_layout)

        import_layout.addWidget(csv_group)

        import_group.setLayout(import_layout)

        advanced_layout.addWidget(import_group)

        ###########################################################################
        ##################### Simulation self.settings #################################
        ###########################################################################

        sim_group = QGroupBox("Simulation settings")

        sim_layout = QFormLayout()

        sim_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        ###########################################################################
        # Neighborhood distribution
        ###########################################################################

        self.poisson_radius = QSpinBox()
        self.poisson_radius.setRange(0, 10000)
        self.poisson_radius.setSuffix(" m")
        self.poisson_radius.setValue(30)
        sim_layout.addRow("PoissonDisk radius:",self.poisson_radius)

        self.poisson_ncandidates = QSpinBox()
        self.poisson_ncandidates.setRange(0, 10000)
        self.poisson_ncandidates.setValue(7)
        sim_layout.addRow("PoissonDisk ncandidates:",self.poisson_ncandidates)

        ###########################################################################
        # Distance self.settings
        ###########################################################################

        self.transit_max_pts_dist = QSpinBox()
        self.transit_max_pts_dist.setRange(0, 10000)
        self.transit_max_pts_dist.setSuffix(" m")
        self.transit_max_pts_dist.setValue(
            self.settings.transit_max_pts_dist
        )

        sim_layout.addRow(
            "Point to network integration distance:",
            self.transit_max_pts_dist
        )

        self.transit_max_move_dist = QSpinBox()
        self.transit_max_move_dist.setRange(0, 10000)
        self.transit_max_move_dist.setSuffix(" m")
        self.transit_max_move_dist.setValue(
            self.settings.transit_max_move_dist
        )

        sim_layout.addRow(
            "Maximum distance to move transit (minimal move):",
            self.transit_max_move_dist
        )

        self.max_dist_transit_network = QSpinBox()
        self.max_dist_transit_network.setRange(0, 10000)
        self.max_dist_transit_network.setSuffix(" m")
        self.max_dist_transit_network.setValue(
            self.settings.max_dist_transit_network
        )

        sim_layout.addRow(
            "Transit to network integration distance:",
            self.max_dist_transit_network
        )

        ###########################################################################
        # Stop constraints
        ###########################################################################

        self.min_distance_stops = QSpinBox()
        self.min_distance_stops.setRange(0, 10000)
        self.min_distance_stops.setSuffix(" m")
        self.min_distance_stops.setValue(
            self.settings.min_distance_stops
        )

        sim_layout.addRow(
            "Minimum bus-stop distance:",
            self.min_distance_stops
        )

        self.max_distance_stops = QSpinBox()
        self.max_distance_stops.setRange(0, 10000)
        self.max_distance_stops.setSuffix(" m")
        self.max_distance_stops.setValue(
            self.settings.max_distance_stops
        )

        sim_layout.addRow(
            "Maximum bus-stop distance:",
            self.max_distance_stops
        )

        ###########################################################################
        # Route constraints
        ###########################################################################

        self.min_stops_in_bus_route = QSpinBox()
        self.min_stops_in_bus_route.setRange(1, 1000)
        self.min_stops_in_bus_route.setValue(
            self.settings.min_stops_in_bus_route
        )

        sim_layout.addRow(
            "Minimum number of bus-stops per route:",
            self.min_stops_in_bus_route
        )

        self.max_stops_in_bus_route = QSpinBox()
        self.max_stops_in_bus_route.setRange(1, 1000)
        self.max_stops_in_bus_route.setValue(
            self.settings.max_stops_in_bus_route
        )

        sim_layout.addRow(
            "Maximum number of bus-stops per route:",
            self.max_stops_in_bus_route
        )

        ###########################################################################
        # Scoring
        ###########################################################################

        self.amenity_to_pop_weight = QSpinBox()
        self.amenity_to_pop_weight.setRange(0, 100000)
        self.amenity_to_pop_weight.setValue(
            self.settings.amenity_to_pop_weight
        )

        sim_layout.addRow(
            "Amenity/population weight:",
            self.amenity_to_pop_weight
        )

        sim_group.setLayout(sim_layout)

        advanced_layout.addWidget(sim_group)

        ###########################################################################
        ##################### Visualization self.settings ###############################
        ###########################################################################

        viz_group = QGroupBox("Visualization self.settings")

        viz_layout = QFormLayout()

        viz_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        ###########################################################################
        # PNG DPI
        ###########################################################################

        self.png_dpi = QSpinBox()
        self.png_dpi.setRange(72, 5000)
        self.png_dpi.setSuffix(" dpi")

        self.png_dpi.setValue(
            self.settings.png_dpi
        )

        viz_layout.addRow(
            "PNG DPI:",
            self.png_dpi
        )

        ###########################################################################
        # Colormap
        ###########################################################################

        self.colormap_box = QComboBox()
        self.colormap_box.setView(QListView())

        self.colormap_box.addItems([
            "viridis",
            "viridis_r",
            "plasma",
            "inferno",
            "magma",
            "cividis",
            "RdBu",
            "RdBu_r",
            "coolwarm",
            "Spectral"
        ])

        self.colormap_box.setCurrentText(
            self.settings.colormap
        )

        viz_layout.addRow(
            "Colormap:",
            self.colormap_box
        )

        ###########################################################################
        # Legend labels
        ###########################################################################

        self.legend_num_labels = QSpinBox()

        self.legend_num_labels.setRange(2, 100)

        self.legend_num_labels.setValue(
            self.settings.legend_num_labels
        )

        viz_layout.addRow(
            "Legend labels:",
            self.legend_num_labels
        )

        viz_group.setLayout(viz_layout)

        advanced_layout.addWidget(viz_group)

        ###########################################################################
        ##################### Finalize advanced ###################################
        ###########################################################################

        advanced.setContentLayout(
            advanced_layout
        )

        dataset_layout.addRow(advanced)

        ###########################################################################
        ##################### Finalize page #######################################
        ###########################################################################

        dataset_group.setLayout(
            dataset_layout
        )

        outer_layout.addWidget(
            dataset_group
        )

        outer_layout.addStretch()

        return page


    def create_simulation_page(self):

        # Basic page parameters
        page = QWidget()
        layout = QVBoxLayout(page)
        group = QGroupBox("Simulation Parameters")
        form = QFormLayout()

        # Every row
        self.city_box = QComboBox()
        self.city_box.setView(QListView())
        form.addRow("City:", self.city_box)

        self.fraction = QDoubleSpinBox()
        self.fraction.setSuffix(" %")
        self.fraction.setRange(0.0, 100.0)
        self.fraction.setSingleStep(1.0)
        self.fraction.setValue(15.0)
        form.addRow("Fraction:", self.fraction)

        #######################################################################
        # Multi simulation self.settings
        #######################################################################

        self.f_start = QDoubleSpinBox()
        self.f_start.setSuffix(" %")
        self.f_start.setRange(0.0, 100.0)
        self.f_start.setValue(0.0)
        self.f_start.setVisible(False)

        self.f_stop = QDoubleSpinBox()
        self.f_stop.setSuffix(" %")
        self.f_stop.setRange(0.0, 100.0)
        self.f_stop.setValue(50.0)
        self.f_stop.setVisible(False)

        self.fn = QSpinBox()
        self.fn.setSuffix(" %")
        self.fn.setRange(1, 1000)
        self.fn.setValue(10)
        self.fn.setVisible(False)

        form.addRow("Fraction start:", self.f_start)
        form.addRow("Fraction stop:", self.f_stop)
        form.addRow("Num simulations:", self.fn)

        #######################################################################
        # Checkboxes
        #######################################################################

        self.use_population = QCheckBox()
        self.use_population.setChecked(True)

        self.use_amenity = QCheckBox()
        self.use_amenity.setChecked(True)

        self.minimal_move = QCheckBox()
        self.minimal_move.setChecked(True)

        self.blank_slate = QCheckBox()

        self.print_progress = QCheckBox()
        self.print_progress.setChecked(True)

        self.svg = QCheckBox()

        form.addRow("Use population:", self.use_population)
        form.addRow("Use amenities:", self.use_amenity)
        form.addRow("Minimal movement:", self.minimal_move)
        form.addRow("Blank slate:", self.blank_slate)
        form.addRow("Print progress:", self.print_progress)
        form.addRow("Export SVG:", self.svg)

        #######################################################################
        # Saving directory
        #######################################################################

        self.save_dir = QLineEdit("results_sim_transit_dist/")

        form.addRow("Output directory:", self.save_dir)

        #######################################################################
        # Run button
        #######################################################################

        self.run_btn = QPushButton("Run simulation")
        self.run_btn.setObjectName("runButton")
        self.run_btn.clicked.connect(self.run_simulation)

        form.addRow(self.run_btn)

        group.setLayout(form)

        layout.addWidget(group)
        layout.addStretch()

        # Get real time output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Create widget real time output
        log_box = CollapsibleBox("Simulation output")
        log_box.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.log_output.setMinimumHeight(250)
        # self.log_output.setBaseSize(1000, 250)
        log_layout = QVBoxLayout()
        log_layout.addWidget(self.log_output)
        log_box.setContentLayout(log_layout)
        # log_box.setBaseSize(1000, 250)
        layout.addWidget(log_box)

        return page

    def prev_clicked(self):

        index = self.pages.currentIndex()

        if index > 0:
            self.pages.setCurrentIndex(index - 1)

    def next_clicked(self):

        index = self.pages.currentIndex()

        if index < self.pages.count() - 1:
            self.pages.setCurrentIndex(index + 1)


    def select_csv(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV dataset",
            "",
            "CSV files (*.csv)"
        )

        if path:
            self.kwb_input.setText(path)

    def select_geopackage(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select geopackage",
            "",
            "Geopackage (*.gpkg)"
        )

        if path:
            self.geo_input.setText(path)

    def load_simulator(self):
        try:
            self.apply_settings()
            self.kwb_path = self.kwb_input.text()
            self.geopackage_path = self.geo_input.text()

            self.statusBar().showMessage("Loading simulator...")

            self.simulator = simulator(self.kwb_path, self.geopackage_path)

            cities = self.simulator.get_cities()

            self.city_box.clear()
            self.city_box.addItems(cities)

            self.statusBar().showMessage(
                f"Simulator loaded successfully ({len(cities)} cities)"
            )

            QMessageBox.information(
                self,
                "Success",
                "Simulator loaded successfully."
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    ############################################################################
    ##################### Simulation ###########################################
    ############################################################################

    def select_simulation(self, index):

        self.simulation = index

        is_multi = index == 1

        self.f_start.setVisible(is_multi)
        self.f_stop.setVisible(is_multi)
        self.fn.setVisible(is_multi)

        self.fraction.setVisible(not is_multi)

    def run_simulation(self):
        """
        Run the selected simulation in a separate thread.
        Real-time stdout is redirected to the GUI log panel.
        """

        self.apply_settings()

        selected_city = (self.city_box.currentText())

        if not hasattr(self, "simulator"):

            self.append_log(
                "ERROR: Simulator not loaded."
            )

            return

        common_kwargs = {

            "use_population":
                self.use_population.isChecked(),

            "use_amenity":
                self.use_amenity.isChecked(),

            "minimal_move":
                self.minimal_move.isChecked(),

            "blank_slate":
                self.blank_slate.isChecked(),

            "print_progress":
                True,

            "saving_dir":
                self.save_dir.text(),

            "svg":
                self.svg.isChecked(),
        }

        if self.simulation == 0:

            common_kwargs["fraction"] = (
                self.fraction.value() / 100
            )

        else:

            common_kwargs["f_start"] = (
                self.f_start.value() / 100
            )

            common_kwargs["f_end"] = (
                self.f_stop.value() / 100
            )

            common_kwargs["fn"] = (
                self.fn.value()
            )

        self.log_output.clear()

        self.run_btn.setEnabled(False)

        self.stout_thread = QThread()

        self.worker = SimulationWorker(
            simulator=self.simulator,
            mode=self.simulation,
            city=selected_city,
            params=common_kwargs
        )

        self.worker.moveToThread(
            self.stout_thread
        )

        self._stdout_backup = sys.stdout

        sys.stdout = StreamRedirector(
            self.worker.log
        )

        self.stout_thread.started.connect(
            self.worker.run
        )

        self.worker.log.connect(
            self.append_log
        )

        self.worker.finished.connect(
            self.stout_thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.stout_thread.finished.connect(
            self.stout_thread.deleteLater
        )

        self.stout_thread.finished.connect(
            self.restore_stdout
        )

        self.stout_thread.finished.connect(
            lambda: self.run_btn.setEnabled(True)
        )

        self.stout_thread.start()

    def stylesheet(self):

        return """
        QMainWindow {
            background-color: #f4f6f8;
        }

        QLabel#headerTitle {
            font-size: 30px;
            font-weight: bold;
            color: #1f2937;
        }

        QLabel#headerSubtitle {
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 15px;
        }

        QLabel#settingsTitle {
            font-size: 22px;
            font-weight: bold;
            padding-bottom: 10px;
        }

        QGroupBox {
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 12px;
            margin-top: 15px;
            padding: 20px;
            font-size: 15px;
            font-weight: bold;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 5px 0 5px;
        }

        QPushButton {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #1d4ed8;
        }

        QPushButton#runButton {
            background-color: #059669;
        }

        QPushButton#runButton:hover {
            background-color: #047857;
        }

        QLineEdit,
        QComboBox {
            background: none;
            padding: 6px 10px;
            border: 1px solid #c5c5c5;
            border-radius: 6px;
            background: white;
            min-height: 24px;
        }

        QComboBox:hover {
            background: none;
            border: 1px solid #999999;
        }

        QComboBox::drop-down {
            background: none;
            border: none;
            width: 24px;
        }

        QComboBox QAbstractItemView {
            border: 1px solid #c5c5c5;
            background: white;
            selection-background-color: #efefef;
            selection-color: red;
            outline: 0px;
        }

        QSpinBox,
        QDoubleSpinBox,
        QTextEdit {
            background: white;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 8px;
            min-height: 30px;
        }

        QScrollArea {
            border: none;
        }
        """

    def add_null_string(self):
        """
        Add a new editable NULL-string item.
        """

        item = QListWidgetItem("")

        item.setFlags(
            item.flags() | Qt.ItemFlag.ItemIsEditable
        )

        self.null_list.addItem(item)

        self.null_list.setCurrentItem(item)

        self.null_list.editItem(item)


    def remove_null_string(self):
        """
        Remove the currently selected NULL-string item.
        """

        current_row = self.null_list.currentRow()

        if current_row >= 0:
            self.null_list.takeItem(current_row)

    def apply_settings(self):
        """
        Apply all GUI settings to the Settings object.
        """

        ###########################################################################
        # Dataset column names
        ###########################################################################

        column_names = {}

        for row in range(self.column_table.rowCount()):

            internal_name = self.column_table.item(row, 0).text()

            dataset_name = self.column_table.item(row, 1).text()

            column_names[internal_name] = dataset_name

        self.settings.dataset_column_names = column_names

        ###########################################################################
        # CSV parsing
        ###########################################################################

        self.settings.dataset_delim = (
            self.delim_box.currentText()
        )

        self.settings.dataset_decimal_separator = (
            self.decimal_box.currentText()
        )

        ###########################################################################
        # NULL strings
        ###########################################################################

        null_strings = []

        for i in range(self.null_list.count()):

            item = self.null_list.item(i)

            null_strings.append(item.text())

        self.settings.dataset_nullstring = null_strings

        ###########################################################################
        # Simulation settings
        ###########################################################################

        self.settings.neighborhood_distribution = (
            lambda a, b, c, d : PoissonDiskDistribution(a, b, c, d,
                                                     radius=self.poisson_radius.value(),
                                                     ncanidates=self.poisson_ncandidates.value())
        )

        self.settings.transit_max_pts_dist = (
            self.transit_max_pts_dist.value()
        )

        self.settings.transit_max_move_dist = (
            self.transit_max_move_dist.value()
        )

        self.settings.max_dist_transit_network = (
            self.max_dist_transit_network.value()
        )

        self.settings.min_distance_stops = (
            self.min_distance_stops.value()
        )

        self.settings.max_distance_stops = (
            self.max_distance_stops.value()
        )

        self.settings.min_stops_in_bus_route = (
            self.min_stops_in_bus_route.value()
        )

        self.settings.max_stops_in_bus_route = (
            self.max_stops_in_bus_route.value()
        )

        self.settings.amenity_to_pop_weight = (
            self.amenity_to_pop_weight.value()
        )

        ###########################################################################
        # Visualization settings
        ###########################################################################

        self.settings.png_dpi = (
            self.png_dpi.value()
        )

        self.settings.colormap = (
            self.colormap_box.currentText()
        )

        self.settings.legend_num_labels = (
            self.legend_num_labels.value()
        )

    def append_log(self, text):
        """
        Append text to the log console.
        """

        self.log_output.append(text)

    def restore_stdout(self):
        """
        Restore original stdout.
        """

        sys.stdout = self._stdout_backup


###############################################################################
##################### Main ####################################################
###############################################################################


if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
