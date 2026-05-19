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
)
from PyQt6.QtCore import Qt

class SettingsWidget(QWidget):

    def __init__(self, settings):
        super().__init__()

        self.settings = settings
        self.widgets = {}

        layout = QFormLayout(self)

        for f in fields(settings):

            name = f.name
            value = getattr(settings, name)
            description = f.metadata.get("description", "")

            widget = self.create_widget(f.type, value)

            if widget is None:
                label = QLabel(f"Unsupported type: {type(value)}")
                layout.addRow(name, label)
                continue

            widget.setToolTip(description)

            self.widgets[name] = widget

            layout.addRow(name, widget)

    def create_widget(self, typ, value):

        if isinstance(value, bool):
            w = QCheckBox()
            w.setChecked(value)
            return w

        elif isinstance(value, int):
            w = QSpinBox()
            w.setRange(-1_000_000, 1_000_000)
            w.setValue(value)
            return w

        elif isinstance(value, float):
            w = QDoubleSpinBox()
            w.setRange(-1e9, 1e9)
            w.setDecimals(6)
            w.setValue(value)
            return w

        elif isinstance(value, str):
            w = QLineEdit(value)
            return w

        elif isinstance(value, list):
            w = QPlainTextEdit("\n".join(map(str, value)))
            return w

        elif isinstance(value, dict):
            import json
            w = QPlainTextEdit(json.dumps(value, indent=2))
            return w

        else:
            return None

    def apply_settings(self):
        for name, widget in self.widgets.items():

            if isinstance(widget, QCheckBox):
                value = widget.isChecked()

            elif isinstance(widget, QSpinBox):
                value = widget.value()

            elif isinstance(widget, QDoubleSpinBox):
                value = widget.value()

            elif isinstance(widget, QLineEdit):
                value = widget.text()

            elif isinstance(widget, QPlainTextEdit):

                text = widget.toPlainText()

                current_value = getattr(self.settings, name)

                if isinstance(current_value, list):
                    value = text.splitlines()

                elif isinstance(current_value, dict):
                    value = json.loads(text)

                else:
                    value = text

            else:
                return None

            setattr(self.settings, name, value)