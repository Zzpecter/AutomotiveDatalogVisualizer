from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QRadioButton, QButtonGroup, QMessageBox)
from PyQt5.QtCore import Qt

from datalog_visualizer.view.plot_canvas import PlotCanvas
from datalog_visualizer.model.data_processor import DataProcessor
from datalog_visualizer.model.strategies import (
    AFRAverageStrategy, HitsStrategy, DeviationStrategy
)
from datalog_visualizer.utils.pyqt_utils import create_combo_box


class VisualizerTab(QWidget):
    def __init__(self, main_window_ref):
        super().__init__()
        self.main_window = main_window_ref
        self.processor = DataProcessor()

        self.matrix_strategies = {
            "Avg AFR": AFRAverageStrategy(),
            "Hit Count": HitsStrategy(),
            "Deviation": DeviationStrategy()
        }

        self.status_label = QLabel()
        self.combo_temp = QComboBox()
        self.combo_tps = QComboBox()
        self.radio_afr = QRadioButton("Avg AFR")
        self.radio_afr.setChecked(True)
        self.radio_hits = QRadioButton("Hit Count")
        self.radio_dev = QRadioButton("Deviation")
        self.view_group = QButtonGroup(self)
        self.btn_plot = QPushButton("PLOT")
        self.btn_reset = QPushButton("RESET")
        self.canvas = PlotCanvas(self)

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.update_status_label(None)
        main_layout.addWidget(self.status_label)
        controls_layout = QHBoxLayout()

        lbl_view = QLabel("View Mode:")
        lbl_view.setStyleSheet("font-weight: bold; margin-left: 20px;")
        self.view_group.addButton(self.radio_afr)
        self.view_group.addButton(self.radio_hits)
        self.view_group.addButton(self.radio_dev)

        self.combo_temp = create_combo_box("Temp:", ["ALL", "WARM", "COLD"], controls_layout)
        self.combo_tps = create_combo_box("TPS:", ["ALL", "CLOSED", ">0%", "WOT"], controls_layout)

        controls_layout.addWidget(lbl_view)
        controls_layout.addWidget(self.radio_afr)
        controls_layout.addWidget(self.radio_hits)
        controls_layout.addWidget(self.radio_dev)

        controls_layout.addSpacing(30)
        self.btn_plot.clicked.connect(self.populate_table)
        self.btn_reset.clicked.connect(self.reset_canvas)
        controls_layout.addWidget(self.btn_plot)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addStretch()

        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.canvas)

    def populate_table(self):
        df = self.main_window.df
        if df.empty:
            QMessageBox.information(self, "Info", "Please OPEN LOG first.")
            return

        filtered_df = self.processor.apply_filters(df, self.combo_temp.currentText(), self.combo_tps.currentText())
        if filtered_df.empty:
            QMessageBox.information(self, "Info", "No data matches current filters.")
            self.canvas.draw_empty_grid()
            return
        val_matrix, txt_matrix, title, cmap, norm, clabel = self.processor.calculate_view_matrix(
            self.processor.process_to_grid(filtered_df),
            self.matrix_strategies[self.view_group.checkedButton().text()],
            self.main_window.get_target_map()
        )

        self.canvas.draw_heatmap(val_matrix, txt_matrix, title, cmap, norm, clabel)

    def update_status_label(self, file_name=None, row_count=None):
        if file_name and row_count is not None:
            text = f"LOG LOADED: {file_name} — {row_count:,} Rows"
            style = "color: black; font-weight: bold; font-size: 14pt; padding: 5px;"
        else:
            text = "NO LOG FILE LOADED"
            style = "color: red; font-weight: bold; font-size: 16pt; padding: 5px; border: 2px solid red;"
        self.status_label.setText(text)
        self.status_label.setStyleSheet(style)

    def reset_canvas(self):
        self.canvas.draw_empty_grid()
