from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from datalog_visualizer.config.constants import X_TICKS, Y_TICKS


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = Figure()
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.setParent(parent)
        self.draw_empty_grid()

    def configure_axes(self):
        self.ax.set_xticks(np.arange(len(X_TICKS)))
        self.ax.set_yticks(np.arange(len(Y_TICKS)))
        self.ax.set_xticklabels(X_TICKS, rotation=45, ha='left')
        self.ax.set_yticklabels(Y_TICKS)
        self.ax.xaxis.tick_top()
        self.ax.xaxis.set_label_position('top')

        self.ax.set_xticks(np.arange(len(X_TICKS) + 1) - 0.5, minor=True)
        self.ax.set_yticks(np.arange(len(Y_TICKS) + 1) - 0.5, minor=True)
        self.ax.grid(which="minor", color="black", linestyle='-', linewidth=1)
        self.ax.tick_params(which="minor", size=0)

        self.ax.set_xlabel("RPM")
        self.ax.set_ylabel("MAP (kPa)")
        self.figure.tight_layout()

    def draw_empty_grid(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        empty_matrix = np.full((len(Y_TICKS), len(X_TICKS)), np.nan)

        self.ax.imshow(empty_matrix, cmap='Greys', aspect='auto', origin='upper')
        self.configure_axes()
        self.ax.set_title("Load Log File to Visualize")
        self.draw()

    def draw_heatmap(self, value_matrix, text_matrix, title, cmap, norm, clabel):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        im = self.ax.imshow(value_matrix, cmap=cmap, norm=norm, origin='upper', aspect='auto')

        self.configure_axes()
        self.ax.set_title(title)

        self.figure.colorbar(im, ax=self.ax).set_label(clabel)

        matrix_shape = value_matrix.shape
        for y in range(matrix_shape[0]):
            for x in range(matrix_shape[1]):
                txt = text_matrix[y, x]
                val = value_matrix[y, x]

                if txt != "":
                    t_color = 'white'
                    if (cmap == 'bwr' and -0.5 < val < 0.5) or \
                            (cmap == 'jet' and 13.0 < val < 15.0):
                        t_color = 'black'

                    self.ax.text(x, y, txt, ha="center", va="center",
                                 color=t_color, fontweight='bold', fontsize=9)
        self.draw()
