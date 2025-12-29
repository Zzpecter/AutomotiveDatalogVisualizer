import pandas as pd
import numpy as np

from datalog_visualizer.config.constants import (
    X_TICKS, Y_TICKS, COL_COOLANT, COL_TPS,
    COL_RPM, COL_MAP, COL_AFR
)
from datalog_visualizer.model.strategies import MatrixStrategy


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

    def calculate_view_matrix(self, grid_data: dict, strategy: MatrixStrategy, target_map: dict) -> tuple:
        if not isinstance(strategy, MatrixStrategy):
            raise ValueError("Invalid calculation strategy provided.")

        return strategy.calculate(grid_data, target_map)
