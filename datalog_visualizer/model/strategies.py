from abc import ABC, abstractmethod
import numpy as np
from matplotlib import colors as mcolors
from datalog_visualizer.config.constants import X_TICKS, Y_TICKS


class MatrixStrategy(ABC):
    def __init__(self):
        self.title = "Abstract Strategy"
        self.cmap = 'gray'
        self.norm = None
        self.val_matrix = np.full((16, 16), np.nan)
        self.txt_matrix = [["" for _ in range(16)] for _ in range(16)]

    @abstractmethod
    def calculate(self, grid_data, target_map=None):
        pass


class AFRAverageStrategy(MatrixStrategy):
    def __init__(self):
        super().__init__()
        self.title = "Average AFR Map"
        self.cmap = 'RdBu_r'
        self.clabel = "Avg. AFR"

    def calculate(self, grid_data, target_map=None):
        for (x, y), values in grid_data.items():
            avg = np.mean(values)
            self.val_matrix[y, x] = avg
            self.txt_matrix[y][x] = f"{avg:.1f}"
        return self.val_matrix, self.txt_matrix, self.title, self.cmap, self.norm, self.clabel


class HitsStrategy(MatrixStrategy):
    def __init__(self):
        super().__init__()
        self.title = "Hit Count Map"
        self.cmap = 'jet'
        self.clabel = "Samples"

    def calculate(self, grid_data, target_map=None):
        for (x, y), values in grid_data.items():
            count = len(values)
            self.val_matrix[y, x] = count
            self.txt_matrix[y][x] = str(count)
        return self.val_matrix, self.txt_matrix, self.title, self.cmap, self.norm, self.clabel


class DeviationStrategy(MatrixStrategy):
    def __init__(self):
        super().__init__()
        self.title = "AFR Deviation (Actual Avg. - Target)"
        self.cmap = 'coolwarm'
        self.clabel = "Error (AFR)"
        self.norm = mcolors.TwoSlopeNorm(vmin=-5, vcenter=0, vmax=5)

    def calculate(self, grid_data, target_map):
        for (x, y), values in grid_data.items():
            rpm, press = X_TICKS[x], Y_TICKS[y]
            target = target_map.get((rpm, press))
            if target:
                dev = np.mean(values) - target
                self.val_matrix[y, x] = dev
                self.txt_matrix[y][x] = f"{dev:+.1f}"
        return self.val_matrix, self.txt_matrix, self.title, self.cmap, self.norm, self.clabel
