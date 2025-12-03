import json
import pandas as pd
import os
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog,
                             QMessageBox, QTabWidget)
from PyQt5.QtCore import QEvent

from datalog_visualizer.config.constants import TARGET_AFR_JSON_PATH
from datalog_visualizer.view.tabs.visualizer_tab import VisualizerTab
from datalog_visualizer.view.tabs.target_map_tab import TargetMapTab
from datalog_visualizer.view.tabs.danger_cfg_tab import DangerCfgTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ME442 Log Visualizer - Zzpecter's GT Turbo")
        self.setGeometry(100, 100, 1200, 800)

        self.df = pd.DataFrame()
        self.target_afr_map = self.load_target_map_from_file()

        self.tabs = QTabWidget()
        self.tab_visualizer = VisualizerTab(self)
        self.tab_targets = TargetMapTab(self)
        self.tab_danger = DangerCfgTab()

        self.tabs.tabBar().installEventFilter(self)
        self.previous_index = self.tabs.currentIndex()
        self.edited = False

        self.initUI()

    def load_target_map_from_file(self):
        map_data = {}
        with open(TARGET_AFR_JSON_PATH, 'r') as f:
            raw_map = json.load(f)
            for key_str, afr in raw_map.items():
                rpm, map_val = map(int, key_str.split(','))
                map_data[(rpm, map_val)] = afr
        return map_data

    def save_target_map_to_file(self, map_data):
        json_ready_map = {}
        for (rpm, map_val), afr in map_data.items():
            key_str = f"{rpm},{map_val}"
            json_ready_map[key_str] = afr

        with open(TARGET_AFR_JSON_PATH, 'w') as f:
            json.dump(json_ready_map, f, indent=4)
        return True

    def initUI(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('FILE')
        open_log_act = QAction('OPEN LOG', self)
        open_log_act.triggered.connect(self.open_log_file)
        save_plot_act = QAction('SAVE PLOT', self)
        save_plot_act.triggered.connect(self.save_current_plot)
        file_menu.addAction(open_log_act)
        file_menu.addAction(save_plot_act)

        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.tab_visualizer, "AFR Visualizer")
        self.tabs.addTab(self.tab_targets, "AFR Target Map")
        self.tabs.addTab(self.tab_danger, "Danger Detection Cfg.")

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseButtonPress and source == self.tabs.tabBar():
            clicked_index = self.tabs.tabBar().tabAt(event.pos())
            if clicked_index != self.tabs.currentIndex():
                if self.edited:
                    reply = QMessageBox.question(self, 'Warning',
                                                 'You have unsaved changes. Are you sure you want to leave this tab?',
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                 QMessageBox.StandardButton.No)

                    if reply == QMessageBox.StandardButton.No:
                        return True
                    else:
                        self.edited = False
                        return False
        return super().eventFilter(source, event)

    def get_target_map(self):
        return self.target_afr_map

    def set_target_map(self, new_map):
        self.target_afr_map = new_map

    def open_log_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV Log", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_name:
            try:
                self.df = pd.read_csv(file_name)
                base_name = os.path.basename(file_name)
                self.tab_visualizer.update_status_label(base_name, len(self.df))

                QMessageBox.information(self, "Success", f"Loaded {len(self.df)} rows.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file: {e}")
                self.tab_visualizer.update_status_label(None)

    def save_current_plot(self):
        self.tab_visualizer.canvas.figure.savefig("plot_output.png")
        QMessageBox.information(self, "Saved", "Plot saved as plot_output.png")
