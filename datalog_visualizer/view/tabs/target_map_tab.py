from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt

from datalog_visualizer.config.constants import X_TICKS, Y_TICKS


class TargetMapTab(QWidget):
    def __init__(self, main_window_ref):
        super().__init__()
        self.main_window = main_window_ref
        self.initUI()
        self.populate_table(self.main_window.get_target_map())

    def initUI(self):
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setRowCount(len(Y_TICKS))
        self.table.setColumnCount(len(X_TICKS))

        self.table.setHorizontalHeaderLabels([str(x) for x in X_TICKS])
        self.table.setVerticalHeaderLabels([str(y) for y in Y_TICKS])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Fill width

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        self.btn_save = QPushButton("SAVE (Update Target)")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white;")
        self.btn_save.clicked.connect(self.save_map)

        self.btn_reset = QPushButton("RESET (Reload Defaults)")
        self.btn_reset.setMinimumHeight(40)
        self.btn_reset.setStyleSheet("font-weight: bold; background-color: #f44336; color: white;")
        self.btn_reset.clicked.connect(self.reset_map)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_reset)

        layout.addLayout(btn_layout)

    def populate_table(self, map_data):
        self.table.blockSignals(True)
        for r, y_val in enumerate(Y_TICKS):
            for c, x_val in enumerate(X_TICKS):
                val = map_data.get((x_val, y_val), -1)
                item = QTableWidgetItem(f"{val:.1f}")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)
        self.table.blockSignals(False)

    def save_map(self):
        new_map = {}
        try:
            for r, y_val in enumerate(Y_TICKS):
                for c, x_val in enumerate(X_TICKS):
                    item = self.table.item(r, c)
                    val = float(item.text())
                    new_map[(x_val, y_val)] = val
            self.main_window.set_target_map(new_map)

            if self.main_window.save_target_map_to_file(new_map):
                QMessageBox.information(self, "Saved", "Target Map Updated in Memory AND Saved to Disk.")
            else:
                QMessageBox.warning(self, "Error", "Target Map Updated in Memory but FAILED to save to disk!")

        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid value found in table. Please enter numbers only.")
            self.reset_map()

    def reset_map(self):
        self.main_window.load_target_map_from_file()
        self.populate_table(self.main_window.get_target_map())
        QMessageBox.information(self, "Reset", "Target AFR Map has been reloaded from last save.")
