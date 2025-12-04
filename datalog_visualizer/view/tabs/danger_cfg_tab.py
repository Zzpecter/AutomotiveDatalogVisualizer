import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QSplitter, QComboBox,
                             QLabel, QGroupBox, QFormLayout, QLineEdit, QPushButton,
                             QMessageBox, QFrame, QAbstractItemView)
from PyQt5.QtCore import Qt
from datalog_visualizer.config.constants import CONFIG_PATH, CONDITIONS_DICT


class DangerCfgTab(QWidget):
    def __init__(self, main_window_ref):
        super().__init__()
        self.main_window = main_window_ref
        self.sensor_data = []

        self.combo_filter = QComboBox()
        self.main_table = QTableWidget()
        self.combo_type = QComboBox()
        self.combo_condition = QComboBox()
        self.btn_create_alert = QPushButton("Create Alert")
        self.btn_update_alert = QPushButton("Update Alert")
        self.btn_remove_alert = QPushButton("Remove Alert")
        self.inp_value = QLineEdit()
        self.btn_save_json = QPushButton("SAVE")
        self.table_alerts = QTableWidget()

        self.initUI()
        self.load_config()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical)

        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        filter_layout = QHBoxLayout()
        lbl_filter = QLabel("Filter Signals:")
        self.combo_filter.addItems(["ALL", "WARNING", "CRITICAL"])
        self.combo_filter.currentTextChanged.connect(self.populate_main_table)
        filter_layout.addWidget(lbl_filter)
        filter_layout.addWidget(self.combo_filter)
        filter_layout.addStretch()

        self.main_table.setColumnCount(7)
        self.main_table.setHorizontalHeaderLabels(["Signal", "Data Type", "Category", "Importance", "Range", "Warning", "Critical"])
        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.main_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.main_table.itemSelectionChanged.connect(self.on_row_selected)
        top_layout.addLayout(filter_layout)
        top_layout.addWidget(self.main_table)

        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        crud_group = QGroupBox("Edit Selected Signal Rule")
        crud_layout = QFormLayout()

        self.combo_type.addItems(["WARNING", "CRITICAL"])
        self.combo_type.setFixedWidth(120)
        self.combo_condition.addItems([
                "EQUAL",
                "NOT EQUAL",
                "LOWER THAN",
                "LOWER-EQUAL THAN",
                "GREATER-EQUAL THAN",
                "GREATER THAN"])
        self.combo_condition.setFixedWidth(240)

        crud_layout.addRow("Type:", self.combo_type)
        crud_layout.addRow("Condition:", self.combo_condition)
        crud_layout.addRow("Value:", self.inp_value)

        btn_layout = QHBoxLayout()
        self.btn_create_alert.clicked.connect(self.create_alert)
        self.btn_update_alert.clicked.connect(self.update_alert)
        self.btn_remove_alert.clicked.connect(self.delete_alert)
        self.btn_remove_alert.setStyleSheet("color: red;")
        btn_layout.addWidget(self.btn_create_alert)
        btn_layout.addWidget(self.btn_update_alert)
        btn_layout.addWidget(self.btn_remove_alert)
        crud_layout.addRow(btn_layout)
        self.btn_save_json.setFixedHeight(40)
        self.btn_save_json.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_save_json.clicked.connect(self.save_config)
        crud_layout.addRow(self.btn_save_json)
        crud_group.setLayout(crud_layout)

        tables_group = QGroupBox("Current Rules")
        tables_layout = QHBoxLayout()

        self.table_alerts.setColumnCount(3)
        self.table_alerts.setHorizontalHeaderLabels(["Type", "Condition", "Value"])
        self.table_alerts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_alerts.setRowCount(1)
        self.table_alerts.verticalHeader().setVisible(False)
        self.table_alerts.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_alerts.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_alerts.itemSelectionChanged.connect(self.on_alert_row_selected)

        tables_layout.addWidget(self.table_alerts)
        tables_group.setLayout(tables_layout)
        bottom_layout.addWidget(crud_group, 4)
        bottom_layout.addWidget(tables_group, 6)

        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def load_config(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r') as f:
                    self.sensor_data = json.load(f)
            else:
                self.sensor_data = []
            self.populate_main_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load config: {e}")

    def populate_main_table(self):
        filter_mode = self.combo_filter.currentText()
        self.main_table.setRowCount(0)

        display_rows = []
        for s, entry in self.sensor_data.items():
            if filter_mode in ("CRITICAL", "WARNING"):
                if len(entry["alerts"]) == 0:
                    continue
                if filter_mode == "CRITICAL" and not any([a["type"] == "CRITICAL" for a in entry["alerts"]]):
                    continue
            display_rows.append(s)

        self.main_table.setRowCount(len(display_rows))

        for row_idx, s in enumerate(display_rows):
            entry = self.sensor_data[s]
            self.main_table.setItem(row_idx, 0, QTableWidgetItem(s))
            self.main_table.setItem(row_idx, 1, QTableWidgetItem(str(entry['data_type'])))
            self.main_table.setItem(row_idx, 2, QTableWidgetItem(str(entry['category'])))
            self.main_table.setItem(row_idx, 3, QTableWidgetItem(str(entry['importance'])))
            self.main_table.setItem(row_idx, 4, QTableWidgetItem(str(entry['range'])))

            # Simplified status for main table
            if len(entry["alerts"]) == 0:
                warn_str = "No"
                crit_str = "No"
            elif any([a["type"] == "CRITICAL" for a in entry["alerts"]]):
                warn_str = "Yes"
                crit_str = "Yes"
            else:
                warn_str = "Yes"
                crit_str = "No"

            item_warn = QTableWidgetItem(warn_str)
            if warn_str == "Yes": item_warn.setForeground(Qt.darkYellow)

            item_crit = QTableWidgetItem(crit_str)
            if crit_str == "Yes": item_crit.setForeground(Qt.red)

            self.main_table.setItem(row_idx, 5, item_warn)
            self.main_table.setItem(row_idx, 6, item_crit)

    def on_row_selected(self):
        selected_items = self.main_table.selectedItems()
        if not selected_items:
            return
        signal = self.main_table.item(selected_items[0].row(), 0).text()
        print(f"Row selection changed! signal: {signal} selected_items {selected_items}")
        self.refresh_alerts_table(self.sensor_data[signal])

    def on_alert_row_selected(self):
        selected_items = self.table_alerts.selectedItems()
        if not selected_items:
            return
        alert_type = self.table_alerts.item(selected_items[0].row(), 0).text()
        condition = self.table_alerts.item(selected_items[0].row(), 1).text()
        value = self.table_alerts.item(selected_items[0].row(), 2).text()

        self.combo_type.setCurrentIndex(self.combo_type.findText(alert_type, Qt.MatchExactly))
        self.combo_condition.setCurrentIndex(self.combo_condition.findText(condition, Qt.MatchExactly))
        self.inp_value.setText(value)

    def refresh_alerts_table(self, entry):
        self.table_alerts.clearContents()
        self.combo_type.setCurrentIndex(-1)
        self.combo_condition.setCurrentIndex(-1)
        self.inp_value.clear()

        alerts = sorted(entry['alerts'], key=lambda a: a['type'])
        self.table_alerts.setRowCount(len(alerts))
        for row, alert in enumerate(alerts):
            self.table_alerts.setItem(row, 0, QTableWidgetItem(str(alert['type'])))
            self.table_alerts.setItem(row, 1, QTableWidgetItem(CONDITIONS_DICT[str(alert['condition'])]))
            self.table_alerts.setItem(row, 2, QTableWidgetItem(str(alert['value'])))

    def get_input_data(self):
        def parse_num(txt):
            if not txt.strip() or txt.strip().lower() == 'none': return None
            try:
                return float(txt)
            except:
                return txt

        return {
            "type": self.combo_type.currentText(),
            "condition": CONDITIONS_DICT[self.combo_condition.currentText()],
            "value": parse_num(self.inp_value.text())
        }

    def create_alert(self, signal):
        if signal not in self.sensor_data.keys:
            return
        data = self.get_input_data()
        if not data['value'] or data['value'] == '':
            QMessageBox.warning(self, "Warning", "value is required.")
            return

        self.sensor_data[signal]['alerts'].append(data)
        self.refresh_alerts_table(self.sensor_data[signal])
        self.main_window.edited = True

    def update_alert(self, signal):
        if signal not in self.sensor_data.keys:
            return
        data = self.get_input_data()
        if not data['value'] or data['value'] == '':
            QMessageBox.warning(self, "Warning", "value is required.")
            return

        idx = self.table_alerts.selectedItems()[0].row()
        self.sensor_data[signal]['alerts'][idx] = data
        self.refresh_alerts_table(self.sensor_data[signal])
        self.main_window.edited = True

    def delete_alert(self, signal):
        idx = self.table_alerts.selectedItems()[0].row()
        self.sensor_data[signal]['alerts'].pop(idx)
        self.refresh_alerts_table(self.sensor_data[signal])
        self.main_window.edited = True

    def save_config(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.sensor_data, f, indent=4)
        QMessageBox.information(self, "Success", "Configuration saved successfully.")
        self.main_window.edited = False
