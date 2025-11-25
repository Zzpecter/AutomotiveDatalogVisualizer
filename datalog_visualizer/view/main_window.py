import sys
import pandas as pd
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QAction, QFileDialog, QMessageBox, QRadioButton, QButtonGroup)

from datalog_visualizer.view.plot_canvas import PlotCanvas
from datalog_visualizer.model.data_processor import DataProcessor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ME442 Log Visualizer - Zzpecter's GT Turbo")
        self.setGeometry(100, 100, 1200, 700)
        self.df = pd.DataFrame()
        self.processor = DataProcessor()

        self.initUI()

    def initUI(self):
        # --- Menu Bar ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('FILE')
        open_log_act = QAction('OPEN LOG', self)
        open_log_act.triggered.connect(self.open_log_file)
        save_plot_act = QAction('SAVE PLOT', self)
        save_plot_act.triggered.connect(self.save_plot)
        file_menu.addAction(open_log_act)
        file_menu.addAction(save_plot_act)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        controls_layout = QHBoxLayout()

        self.combo_temp = self._create_combo_box("Temp:", ["ALL", "WARM", "COLD"], controls_layout)
        self.combo_tps = self._create_combo_box("TPS:", ["ALL", "CLOSED", ">0%", "WOT"], controls_layout)

        lbl_view = QLabel("View Mode:")
        lbl_view.setStyleSheet("font-weight: bold; margin-left: 20px;")

        self.radio_afr = QRadioButton("Avg AFR")
        self.radio_afr.setChecked(True)
        self.radio_hits = QRadioButton("Hit Count")
        self.radio_dev = QRadioButton("Deviation")
        self.view_group = QButtonGroup(self)
        self.view_group.addButton(self.radio_afr)
        self.view_group.addButton(self.radio_hits)
        self.view_group.addButton(self.radio_dev)

        controls_layout.addWidget(lbl_view)
        controls_layout.addWidget(self.radio_afr)
        controls_layout.addWidget(self.radio_hits)
        controls_layout.addWidget(self.radio_dev)

        controls_layout.addSpacing(30)
        self.btn_plot = QPushButton("PLOT")
        self.btn_plot.clicked.connect(self.plot_data)
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.clicked.connect(self.reset_canvas)
        controls_layout.addWidget(self.btn_plot)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addStretch()

        self.canvas = PlotCanvas(self)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.canvas)

    def _create_combo_box(self, label_text, items, layout):
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-weight: bold; margin-left: 10px;")
        combo = QComboBox()
        combo.addItems(items)
        combo.setFixedWidth(80)

        layout.addWidget(lbl)
        layout.addWidget(combo)
        return combo

    def get_view_mode(self):
        if self.radio_afr.isChecked(): return 'afr'
        if self.radio_hits.isChecked(): return 'hits'
        if self.radio_dev.isChecked(): return 'dev'
        return 'afr'

    def open_log_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV Log", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_name:
            try:
                self.df = pd.read_csv(file_name)
                QMessageBox.information(self, "Success", f"Loaded {len(self.df)} rows.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file: {e}")

    def plot_data(self):
        if self.df.empty:
            QMessageBox.information(self, "Info", "Please OPEN LOG first.")
            return

        temp_sel = self.combo_temp.currentText()
        tps_sel = self.combo_tps.currentText()
        view_mode = self.get_view_mode()

        filtered_df = self.processor.apply_filters(self.df, temp_sel, tps_sel)

        if filtered_df.empty:
            QMessageBox.information(self, "Info", "No data matches current filters.")
            self.canvas.draw_empty_grid()
            return

        grid_data = self.processor.process_to_grid(filtered_df)

        filters = {'temp': temp_sel, 'tps': tps_sel}

        value_matrix, text_matrix, title, cmap, norm, clabel = \
            self.processor.calculate_view_matrix(grid_data, view_mode, filters)

        self.canvas.draw_heatmap(value_matrix, text_matrix, title, cmap, norm, clabel)

    def reset_canvas(self):
        self.canvas.draw_empty_grid()

    def save_plot(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Files (*.png)", options=options)
        if filename:
            self.canvas.figure.savefig(filename)
