from dataclasses import fields
import json
from PyQt6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QPlainTextEdit,
    QLabel,
    QToolButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QFrame,
    QTextEdit,
)
from PyQt6.QtCore import (
    Qt,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QAbstractAnimation,
)


class CollapsibleBox(QWidget):

    def __init__(self, title="", parent=None):
        super().__init__(parent)

        #######################################################################
        # Toggle button
        #######################################################################

        self.toggle_button = QToolButton()
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
        content.setLayout(content_layout)

        self.content_area.setWidget(content)

        collapsed_height = 0
        content_height = content.sizeHint().height()

        self.content_animation.setStartValue(collapsed_height)
        self.content_animation.setEndValue(content_height)