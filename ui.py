import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, 
                             QAction, QFileDialog, QMessageBox, QRadioButton, QButtonGroup)
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from constants import TARGET_AFR_MAP 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ECU Map Analyzer - Table View")
        self.setGeometry(100, 100, 1200, 700) 

        self.df = None 

        # Custom Grid Coordinates
        self.x_ticks = [500, 800, 1100, 1400, 2000, 2600, 3100, 3700, 
                        4300, 4900, 5400, 6000, 6500, 7000, 7200, 7500]
        self.y_ticks = [20, 25, 30, 45, 55, 65, 75, 85, 95, 100, 
                        120, 140, 160, 190, 225, 250]

        self.initUI()

    def initUI(self):
        # --- Menu Bar ---
        menubar = self.menuBar()
        file_menu = menubar.addMenu('FILE')
        open_log_act = QAction('OPEN LOG', self)
        open_log_act.triggered.connect(self.open_log_file)
        save_plot_act = QAction('SAVE PLOT', self)
        save_plot_act.triggered.connect(self.save_plot)
        file_menu.addAction(open_log_act)
        file_menu.addAction(save_plot_act)

        # --- Central Widget ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        controls_layout = QHBoxLayout()

        # 1. Temp Filter
        lbl_temp = QLabel("Temp:")
        lbl_temp.setStyleSheet("font-weight: bold;")
        self.combo_temp = QComboBox()
        self.combo_temp.addItems(["ALL", "WARM", "COLD"])
        self.combo_temp.setFixedWidth(80)

        # 2. TPS Filter
        lbl_tps = QLabel("TPS:")
        lbl_tps.setStyleSheet("font-weight: bold; margin-left: 10px;")
        self.combo_tps = QComboBox()
        self.combo_tps.addItems(["ALL", "CLOSED", ">0%", "WOT"])
        self.combo_tps.setFixedWidth(80)

        # 3. View Mode Toggle
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

        # 4. Action Buttons
        self.btn_plot = QPushButton("PLOT")
        self.btn_plot.clicked.connect(self.plot_data)
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.clicked.connect(self.reset_canvas)

        controls_layout.addWidget(lbl_temp)
        controls_layout.addWidget(self.combo_temp)
        controls_layout.addWidget(lbl_tps)
        controls_layout.addWidget(self.combo_tps)
        
        controls_layout.addWidget(lbl_view)
        controls_layout.addWidget(self.radio_afr)
        controls_layout.addWidget(self.radio_hits)
        controls_layout.addWidget(self.radio_dev)
        
        controls_layout.addSpacing(30)
        controls_layout.addWidget(self.btn_plot)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addStretch()

        # --- Canvas ---
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        # Don't draw grid immediately, wait for data or reset
        self.setup_empty_grid()

        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.canvas)

    def setup_empty_grid(self):
        """Initializes an empty table view."""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        # Create empty matrix
        empty_matrix = np.full((len(self.y_ticks), len(self.x_ticks)), np.nan)
        
        self.ax.imshow(empty_matrix, cmap='Greys', aspect='auto', origin='upper')
        self.configure_axes()
        self.ax.set_title("No Data Loaded")
        self.canvas.draw()

    def configure_axes(self):
        """Common axis setup for table view"""
        # Set ticks to be the indices (0, 1, 2...)
        self.ax.set_xticks(np.arange(len(self.x_ticks)))
        self.ax.set_yticks(np.arange(len(self.y_ticks)))
        
        # Label the ticks with the actual values
        self.ax.set_xticklabels(self.x_ticks)
        self.ax.set_yticklabels(self.y_ticks)

        # Move X Axis to Top
        self.ax.xaxis.tick_top()
        self.ax.xaxis.set_label_position('top')

        # Draw Grid lines between the cells (at x.5 indices)
        # We use minor ticks for the grid lines to center the labels
        self.ax.set_xticks(np.arange(len(self.x_ticks) + 1) - 0.5, minor=True)
        self.ax.set_yticks(np.arange(len(self.y_ticks) + 1) - 0.5, minor=True)
        self.ax.grid(which="minor", color="black", linestyle='-', linewidth=1)
        self.ax.tick_params(which="minor", size=0) # Hide minor tick marks

        self.ax.set_xlabel("RPM")
        self.ax.set_ylabel("MAP (kPa)")

    def open_log_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV Log", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                self.df = pd.read_csv(file_name)
                print(f"Loaded {len(self.df)} rows.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file: {e}")

    def plot_data(self):
        if self.df is None:
            QMessageBox.information(self, "Info", "Please OPEN LOG first.")
            return

        # 1. Filter Data
        filtered_df = self.df.copy()
        
        # Temp Filter
        temp_sel = self.combo_temp.currentText()
        if temp_sel == 'COLD': filtered_df = filtered_df[filtered_df[' Coolant Temp.'] < 40]
        elif temp_sel == 'WARM': filtered_df = filtered_df[filtered_df[' Coolant Temp.'] >= 40]

        # TPS Filter
        tps_sel = self.combo_tps.currentText()
        if tps_sel == 'CLOSED': filtered_df = filtered_df[filtered_df[' TPS'] == 0]
        elif tps_sel == '>0%': filtered_df = filtered_df[filtered_df[' TPS'] > 0]
        elif tps_sel == 'WOT': filtered_df = filtered_df[filtered_df[' TPS'] >= 90]

        if filtered_df.empty:
            QMessageBox.information(self, "Info", "No data matches current filters.")
            return

        # 2. Aggregate Data into Matrix
        # We create a 2D numpy array for values, and another for text
        matrix_shape = (len(self.y_ticks), len(self.x_ticks))
        value_matrix = np.full(matrix_shape, np.nan)
        text_matrix = np.full(matrix_shape, "", dtype=object)

        # Temporary storage for aggregation
        grid_data = {} # Key: (x_idx, y_idx), Value: [List of AFRs]

        np_x_ticks = np.array(self.x_ticks)
        np_y_ticks = np.array(self.y_ticks)

        # Process Data
        for _, row in filtered_df.iterrows():
            raw_rpm = row[' RPM']
            raw_map = row[' MAP']
            raw_afr = row[' Int. WB AFR']

            # Find indices of nearest grid points
            idx_x = (np.abs(np_x_ticks - raw_rpm)).argmin()
            idx_y = (np.abs(np_y_ticks - raw_map)).argmin()

            key = (idx_x, idx_y)
            if key not in grid_data: grid_data[key] = []
            grid_data[key].append(raw_afr)

        # 3. Fill Matrices based on Mode
        mode_afr = self.radio_afr.isChecked()
        mode_hits = self.radio_hits.isChecked()
        mode_dev = self.radio_dev.isChecked()
        
        norm = None
        cmap = 'jet'
        title = ""

        # Determine Ranges for colors
        for (idx_x, idx_y), afr_list in grid_data.items():
            avg_afr = sum(afr_list) / len(afr_list)
            
            val_to_plot = np.nan
            text_to_show = ""

            if mode_afr:
                val_to_plot = avg_afr
                text_to_show = f"{avg_afr:.1f}"
                title = "Average AFR"
                cmap = 'jet'

            elif mode_hits:
                val_to_plot = len(afr_list)
                text_to_show = str(val_to_plot)
                title = "Hit Count"
                cmap = 'viridis'

            elif mode_dev:
                # Get Target based on the VALUES at this index
                grid_rpm_val = self.x_ticks[idx_x]
                grid_map_val = self.y_ticks[idx_y]
                
                target = TARGET_AFR_MAP[grid_rpm_val][grid_map_val]
                diff = avg_afr - target
                
                val_to_plot = diff
                text_to_show = f"{diff:+.1f}"
                title = "Deviation (Actual - Target)"
                cmap = 'bwr' # Blue-White-Red
                norm = mcolors.TwoSlopeNorm(vmin=-1.5, vcenter=0, vmax=1.5)

            # Note on Indexing: Matplotlib imshow is [row, col] -> [y, x]
            value_matrix[idx_y, idx_x] = val_to_plot
            text_matrix[idx_y, idx_x] = text_to_show

        # 4. Draw Plot
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        # Draw Heatmap (origin='upper' puts index 0 at the top)
        # aspect='auto' ensures cells stretch to fill window
        im = self.ax.imshow(value_matrix, cmap=cmap, norm=norm, origin='upper', aspect='auto')
        
        # Configure Labels and Grid
        self.configure_axes()
        self.ax.set_title(title)

        # Add Colorbar
        cbar = self.figure.colorbar(im, ax=self.ax)
        cbar.set_label('Value')

        # 5. Draw Text Overlay
        # Loop through every cell
        for y in range(matrix_shape[0]):
            for x in range(matrix_shape[1]):
                txt = text_matrix[y, x]
                val = value_matrix[y, x]
                
                if txt != "":
                    # Determine text color based on background
                    t_color = 'white'
                    if mode_dev:
                        # If deviation is near 0 (white background), use black text
                        if -0.5 < val < 0.5:
                            t_color = 'black'
                    elif mode_afr:
                        # Yellow/Green areas of 'jet' can be bright
                        if 13.0 < val < 15.0:
                            t_color = 'black'
                            
                    self.ax.text(x, y, txt, ha="center", va="center", 
                                 color=t_color, fontweight='bold', fontsize=9)

        self.canvas.draw()

    def reset_canvas(self):
        self.setup_empty_grid()

    def save_plot(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Files (*.png)", options=options)
        if fileName:
            self.figure.savefig(fileName)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())