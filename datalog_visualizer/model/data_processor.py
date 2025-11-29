import pandas as pd
import numpy as np
from matplotlib import colors as mcolors

from datalog_visualizer.config.constants import (
    X_TICKS, Y_TICKS, TARGET_AFR_MAP, COL_COOLANT, COL_TPS,
    COL_RPM, COL_MAP, COL_AFR
)


class DataProcessor:
    def __init__(self):
        self.np_x_ticks = np.array(X_TICKS)
        self.np_y_ticks = np.array(Y_TICKS)
        self.matrix_shape = (len(Y_TICKS), len(X_TICKS))

    def _apply_coolant_filter(self, df: pd.DataFrame, temp_mode: str) -> pd.DataFrame:
        if temp_mode == 'COLD':
            return df[df[COL_COOLANT] < 40]
        elif temp_mode == 'WARM':
            return df[df[COL_COOLANT] >= 40]
        return df

    def _apply_tps_filter(self, df: pd.DataFrame, tps_mode: str) -> pd.DataFrame:
        if tps_mode == 'CLOSED':
            return df[df[COL_TPS] == 0]
        elif tps_mode == '>0%':
            return df[df[COL_TPS] > 0]
        elif tps_mode == 'WOT':
            return df[df[COL_TPS] >= 90]
        return df

    def apply_filters(self, df: pd.DataFrame, temp_mode: str, tps_mode: str) -> pd.DataFrame:
        if df.empty:
            return df

        df = self._apply_coolant_filter(df, temp_mode)
        df = self._apply_tps_filter(df, tps_mode)
        return df

    def process_to_grid(self, df: pd.DataFrame) -> dict:
        grid_data = {}

        for _, row in df.iterrows():
            raw_rpm = row[COL_RPM]
            raw_map = row[COL_MAP]
            raw_afr = row[COL_AFR]

            idx_x = (np.abs(self.np_x_ticks - raw_rpm)).argmin()
            idx_y = (np.abs(self.np_y_ticks - raw_map)).argmin()

            key = (idx_x, idx_y)
            if key not in grid_data:
                grid_data[key] = []
            grid_data[key].append(raw_afr)

        return grid_data

    def calculate_view_matrix(self, grid_data: dict, view_mode: str, filters: dict) -> tuple:
        value_matrix = np.full(self.matrix_shape, np.nan)
        text_matrix = np.full(self.matrix_shape, "", dtype=object)

        norm = None
        cmap = 'jet'
        title = f"Data ({filters['temp']}, {filters['tps']})"
        clabel = ""

        for (idx_x, idx_y), afr_list in grid_data.items():
            avg_afr = sum(afr_list) / len(afr_list)
            val_to_plot = np.nan
            text_to_show = ""

            if view_mode == 'afr':
                val_to_plot = avg_afr
                text_to_show = f"{avg_afr:.1f}"
                title = f"Average AFR ({filters['temp']}, {filters['tps']})"
                cmap = 'jet'
                clabel = "AFR"

            elif view_mode == 'hits':
                val_to_plot = len(afr_list)
                text_to_show = str(val_to_plot)
                title = f"Hit Count ({filters['temp']}, {filters['tps']})"
                cmap = 'viridis'
                clabel = "Samples"

            elif view_mode == 'dev':
                target = TARGET_AFR_MAP[idx_x][idx_y]
                diff = avg_afr - target

                val_to_plot = diff
                text_to_show = f"{diff:+.1f}"
                title = f"AFR Deviation Map (Actual - Target) ({filters['temp']}, {filters['tps']})"
                cmap = 'bwr'
                clabel = "AFR Deviation"
                norm = mcolors.TwoSlopeNorm(vmin=-2.5, vcenter=0, vmax=2.5)

            value_matrix[idx_y, idx_x] = val_to_plot
            text_matrix[idx_y, idx_x] = text_to_show

        return value_matrix, text_matrix, title, cmap, norm, clabel
