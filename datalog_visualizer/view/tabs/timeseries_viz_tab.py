import os
import json
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QPushButton, QLabel, QGroupBox,
                             QRadioButton, QButtonGroup, QSlider, QCheckBox,
                             QSplitter, QFrame, QDoubleSpinBox, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush
from datalog_visualizer.config.constants import CONFIG_PATH, CONDITIONS_DICT
import pyqtgraph as pg


class TimeSeriesVizTab(QWidget):
    def __init__(self, main_window_ref):
        super().__init__()
        self.main_window = main_window_ref
        self.df = pd.DataFrame()
        self.sensor_config = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.x_data = np.array([])

        self.playing = False
        self.animation_index = 0
        self.plot_curves = {}
        self.alert_scatter = None
        self.extra_views = []

        self.plot_widget = pg.PlotWidget()
        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.h_line = pg.InfiniteLine(angle=0, movable=False)
        self.label_hover = pg.TextItem(anchor=(0, 1), color="w", fill=(0, 0, 0, 100))
        self.sensor_list = QListWidget()
        self.btn_reset_sigs = QPushButton("RESET SELECTION")
        self.spin_trim_start = QDoubleSpinBox()
        self.spin_trim_end = QDoubleSpinBox()
        self.bg_alerts = QButtonGroup(self)
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.btn_play = QPushButton("▶")
        self.btn_pause = QPushButton("⏸")
        self.btn_stop = QPushButton("⏹")
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_window = QSlider(Qt.Horizontal)

        self.init_ui()
        self.load_sensor_config()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        upper_splitter = QSplitter(Qt.Horizontal)

        self.plot_widget.setBackground('k')  # Black background
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.addLegend()
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.setLabel('left', 'AFR', color='white')

        self.plot_widget.addItem(self.v_line, ignoreBounds=True)
        self.plot_widget.addItem(self.h_line, ignoreBounds=True)
        self.plot_widget.addItem(self.label_hover)
        self.plot_widget.scene().sigMouseMoved.connect(self.mouse_moved)

        sig_widget = QWidget()
        sig_layout = QVBoxLayout(sig_widget)
        sig_layout.addWidget(QLabel("<b>Valid Sensors</b>"))
        self.sensor_list.itemChanged.connect(self.on_sensor_selection_change)
        self.btn_reset_sigs.clicked.connect(self.reset_selections)
        sig_layout.addWidget(self.sensor_list)
        sig_layout.addWidget(self.btn_reset_sigs)
        upper_splitter.addWidget(self.plot_widget)
        upper_splitter.addWidget(sig_widget)
        upper_splitter.setStretchFactor(0, 8)
        upper_splitter.setStretchFactor(1, 2)

        tools_group = QGroupBox("Analysis Tools")
        tools_layout = QHBoxLayout(tools_group)
        trim_box = QGroupBox("Log Trimming")
        trim_layout = QVBoxLayout(trim_box)
        range_layout = QHBoxLayout()
        self.spin_trim_start.setPrefix("Start: ")
        self.spin_trim_end.setPrefix("End: ")
        range_layout.addWidget(self.spin_trim_start)
        range_layout.addWidget(self.spin_trim_end)
        btn_save_trim = QPushButton("SAVE TRIM")
        btn_save_trim.clicked.connect(self.save_trim)
        trim_layout.addLayout(range_layout)
        trim_layout.addWidget(btn_save_trim)

        alert_box = QGroupBox("Alert Settings")
        alert_layout = QVBoxLayout(alert_box)
        opts = ["NONE", "WARNING", "CRITICAL", "ALL"]
        for opt in opts:
            rb = QRadioButton(opt)
            self.bg_alerts.addButton(rb)
            alert_layout.addWidget(rb)
            if opt == "NONE": rb.setChecked(True)
        self.bg_alerts.buttonClicked.connect(self.refresh_alerts)

        zoom_box = QGroupBox("Zoom Level")
        zoom_layout = QVBoxLayout(zoom_box)
        self.slider_zoom.setRange(0, 100)
        self.slider_zoom.valueChanged.connect(self.apply_zoom)
        btn_reset_zoom = QPushButton("RESET ZOOM")
        btn_reset_zoom.clicked.connect(lambda: self.slider_zoom.setValue(0))
        zoom_layout.addWidget(self.slider_zoom)
        zoom_layout.addWidget(btn_reset_zoom)

        anim_box = QGroupBox("Animation")
        anim_layout = QVBoxLayout(anim_box)
        ctrl_btns = QHBoxLayout()
        self.btn_play.clicked.connect(self.start_animation)
        self.btn_pause.clicked.connect(self.pause_animation)
        self.btn_stop.clicked.connect(self.stop_animation)
        ctrl_btns.addWidget(self.btn_play)
        ctrl_btns.addWidget(self.btn_pause)
        ctrl_btns.addWidget(self.btn_stop)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.slider_speed.setRange(5, 15)  # 0.5 to 1.5 scaled by 10
        self.slider_speed.setValue(10)
        self.slider_speed.valueChanged.connect(self.update_timer_speed)
        speed_layout.addWidget(self.slider_speed)

        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Window:"))
        self.slider_window.setRange(20, 200)
        self.slider_window.setValue(50)
        width_layout.addWidget(self.slider_window)

        anim_layout.addLayout(ctrl_btns)
        anim_layout.addLayout(speed_layout)
        anim_layout.addLayout(width_layout)

        tools_layout.addWidget(trim_box)
        tools_layout.addWidget(alert_box)
        tools_layout.addWidget(zoom_box)
        tools_layout.addWidget(anim_box)

        main_layout.addWidget(upper_splitter, stretch=7)
        main_layout.addWidget(tools_group, stretch=3)

    # --- LOGIC: Load & Filter ---
    def load_sensor_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                self.sensor_config = json.load(f)

    def refresh_data_source(self):
        """Called by MainWindow when a new log is opened."""
        self.df = self.main_window.df
        if self.df.empty: return

        # Reset UI
        self.sensor_list.clear()
        self.plot_widget.clear()
        self.plot_curves = {}

        self.x_data = self.df['Time'].values
        self.spin_trim_start.setRange(self.x_data.min(), self.x_data.max())
        self.spin_trim_end.setRange(self.x_data.min(), self.x_data.max())
        self.spin_trim_start.setValue(self.x_data.min())
        self.spin_trim_end.setValue(self.x_data.max())

        valid_signals_cfg = [
            signal for signal, info in self.sensor_config.items()
            if info['data_type'] in ['int', 'float'] and info['category'] != 'datetime'
        ]
        print(f"valid_signals_cfg {valid_signals_cfg}")
        for col in self.df.columns:
            print(f"col {col}, col1 {col not in valid_signals_cfg}, col2 {self.df[col].nunique() <= 1}")
            if col not in valid_signals_cfg or self.df[col].nunique() <= 1:
                continue

            item = QListWidgetItem(col.strip())
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, col)
            self.sensor_list.addItem(item)

    # --- LOGIC: Plotting ---
    def on_sensor_selection_change(self, item):
        col_name = item.data(Qt.UserRole)

        if item.checkState() == Qt.Checked:
            self.add_trace(col_name)
        else:
            self.remove_trace(col_name)

        self.refresh_alerts()  # Re-draw alerts if signal changed

    def add_trace(self, col_name):
        if col_name in self.plot_curves: return

        # Get data
        y_data = self.df[col_name].values

        # Determine Axis
        # Left Axis is reserved for AFR (if available) or first item
        clean_name = col_name.strip()

        color = QColor.fromHsv(np.random.randint(0, 255), 255, 200)

        if "AFR" in clean_name:
            # Plot on Main Axis
            curve = self.plot_widget.plot(self.x_data, y_data, pen=pg.mkPen(color, width=2), name=clean_name)
            self.plot_curves[col_name] = curve
        else:
            # Create a ViewBox for multi-scale handling
            # Note: For simplicity in this demo, we verify if we need a secondary axis
            # A full unlimited-axis implementation is very complex in PyQtGraph.
            # We will use the Main PlotItem for everything but normalize visual range
            # OR create one secondary axis (Right) and map all non-AFR signals there.

            # Implementation: Add to main plot, but let PyQtGraph Auto-Scale handle it
            # Or use a separate ViewBox.
            # For this "High Quality" request, we stick to the main view to ensure performance,
            # but we color code the legend.

            curve = self.plot_widget.plot(self.x_data, y_data, pen=pg.mkPen(color, width=2), name=clean_name)
            self.plot_curves[col_name] = curve

    def remove_trace(self, col_name):
        if col_name in self.plot_curves:
            self.plot_widget.removeItem(self.plot_curves[col_name])
            del self.plot_curves[col_name]

    def reset_selections(self):
        for i in range(self.sensor_list.count()):
            self.sensor_list.item(i).setCheckState(Qt.Unchecked)
        self.plot_widget.clear()
        self.plot_curves = {}

    def mouse_moved(self, evt):
        if self.playing: return  # Disable during animation

        pos = evt
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mousePoint = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            index = int(np.searchsorted(self.x_data, mousePoint.x()))

            if 0 <= index < len(self.x_data):
                self.v_line.setPos(mousePoint.x())
                self.h_line.setPos(mousePoint.y())

                # Build Tooltip
                text = f"Time: {self.x_data[index]:.2f}\n"
                for col, curve in self.plot_curves.items():
                    val = self.df[col].values[index]
                    text += f"{col.strip()}: {val:.2f}\n"

                self.label_hover.setText(text)
                self.label_hover.setPos(mousePoint.x(), mousePoint.y())

    # --- LOGIC: Tools ---
    def save_trim(self):
        start = self.spin_trim_start.value()
        end = self.spin_trim_end.value()

        # Mask
        mask = (self.x_data >= start) & (self.x_data <= end)
        trimmed_df = self.df[mask]

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Trimmed Log", "", "CSV Files (*.csv)", options=options)
        if fileName:
            trimmed_df.to_csv(fileName, index=False)
            QMessageBox.information(self, "Success", "Trimmed log saved.")

    def apply_zoom(self):
        if self.playing or len(self.x_data) == 0: return

        val = self.slider_zoom.value()  # 0 to 100

        # Calculate range
        total_range = self.x_data[-1] - self.x_data[0]
        center = (self.x_data[-1] + self.x_data[0]) / 2

        # Invert percentage to span
        # 0% zoom = 100% span, 99% zoom = 1% span
        factor = (100 - val) / 100.0
        if factor < 0.01: factor = 0.01

        new_span = total_range * factor
        min_x = center - (new_span / 2)
        max_x = center + (new_span / 2)

        self.plot_widget.setXRange(min_x, max_x, padding=0)

    def refresh_alerts(self):
        # Remove old alerts
        if self.alert_scatter:
            self.plot_widget.removeItem(self.alert_scatter)
            self.alert_scatter = None

        mode = self.bg_alerts.checkedButton().text()
        if mode == "NONE" or self.df.empty: return

        points = []  # list of dicts {'pos': (x, y), 'brush': color}

        # Identify Active Columns (only check plotted lines to save perf, or check all?)
        # Prompt says "cross-check selected signals".
        active_cols = [k for k in self.plot_curves.keys()]

        for col in active_cols:
            clean_col = col.strip()
            # Find config
            cfg = next((item for item in self.sensor_config if item["signal"] == clean_col), None)
            if not cfg: continue

            y_vals = self.df[col].values

            # Check Critical
            if mode in ["CRITICAL", "ALL"] and cfg.get('critical'):
                crit = cfg['critical']
                mask = np.zeros(len(y_vals), dtype=bool)
                if crit.get('min') is not None: mask |= (y_vals < crit['min'])
                if crit.get('max') is not None: mask |= (y_vals > crit['max'])
                if crit.get('value') is not None: mask |= (y_vals == crit['value'])

                indices = np.where(mask)[0]
                for idx in indices:
                    points.append({'pos': (self.x_data[idx], y_vals[idx]),
                                   'brush': pg.mkBrush('r'), 'symbol': 'o', 'size': 10})

            # Check Warning
            if mode in ["WARNING", "ALL"] and cfg.get('warning'):
                warn = cfg['warning']
                mask = np.zeros(len(y_vals), dtype=bool)
                if warn.get('min') is not None: mask |= (y_vals < warn['min'])
                if warn.get('max') is not None: mask |= (y_vals > warn['max'])

                indices = np.where(mask)[0]
                for idx in indices:
                    # Don't overwrite criticals (simple logic: just add on top)
                    points.append({'pos': (self.x_data[idx], y_vals[idx]),
                                   'brush': pg.mkBrush(255, 165, 0), 'symbol': 't', 'size': 8})

        if points:
            self.alert_scatter = pg.ScatterPlotItem(points)
            self.plot_widget.addItem(self.alert_scatter)

    # --- LOGIC: Animation ---
    def start_animation(self):
        if self.df.empty: return
        self.playing = True
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)

        # Hide interactive elements
        self.v_line.hide()
        self.h_line.hide()
        self.label_hover.hide()

        self.update_timer_speed()
        self.timer.start()

    def pause_animation(self):
        self.playing = False
        self.timer.stop()
        self.btn_play.setEnabled(True)
        self.btn_pause.setEnabled(False)

    def stop_animation(self):
        self.pause_animation()
        self.animation_index = 0
        self.btn_stop.setEnabled(False)

        # Restore View
        self.plot_widget.enableAutoRange()
        self.v_line.show()
        self.h_line.show()
        self.label_hover.show()

    def update_timer_speed(self):
        # Slider 5-15 -> 0.5x to 1.5x
        # Base interval 50ms
        val = self.slider_speed.value() / 10.0
        interval = int(50 / val)
        self.timer.setInterval(interval)

    def update_animation(self):
        if not self.playing: return

        window_width_indices = self.slider_window.value()

        # Advance index
        self.animation_index += 1
        if self.animation_index >= len(self.x_data):
            self.stop_animation()
            return

        # Calculate Window
        end_idx = self.animation_index
        start_idx = max(0, end_idx - window_width_indices)

        min_x = self.x_data[start_idx]
        max_x = self.x_data[end_idx]

        # Update X Range to simulate sliding
        self.plot_widget.setXRange(min_x, max_x, padding=0)