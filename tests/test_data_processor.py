import unittest
import pandas as pd
from datalog_visualizer.model.data_processor import DataProcessor
from datalog_visualizer.config.constants import (
    COL_RPM, COL_MAP, COL_AFR, COL_COOLANT, COL_TPS
)


class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DataProcessor()

        data = {
            COL_RPM: [800, 2000, 6000, 800],
            COL_MAP: [20, 45, 100, 20],
            COL_AFR: [14.7, 13.5, 12.0, 15.3],
            COL_COOLANT: [30, 85, 90, 20],
            COL_TPS: [0, 15, 100, 0]
        }
        self.df = pd.DataFrame(data)

    def test_apply_coolant_filter(self):
        df_cold = self.processor.apply_filters(self.df, 'COLD', 'ALL')
        self.assertTrue((df_cold[COL_COOLANT] < 40).all())
        self.assertEqual(len(df_cold), 2)

        df_warm = self.processor.apply_filters(self.df, 'WARM', 'ALL')
        self.assertTrue((df_warm[COL_COOLANT] >= 40).all())
        self.assertEqual(len(df_warm), 2)

    def test_apply_tps_filter(self):
        df_closed = self.processor.apply_filters(self.df, 'ALL', 'CLOSED')
        self.assertTrue((df_closed[COL_TPS] == 0).all())
        self.assertEqual(len(df_closed), 2)

        df_wot = self.processor.apply_filters(self.df, 'ALL', 'WOT')
        self.assertTrue((df_wot[COL_TPS] >= 90).all())
        self.assertEqual(len(df_wot), 1)

    def test_process_to_grid(self):
        grid_data = self.processor.process_to_grid(self.df)
        key = (1, 0)  # (x_idx, y_idx)

        self.assertIn(key, grid_data)
        self.assertEqual(len(grid_data[key]), 2)
        self.assertIn(14.7, grid_data[key])
        self.assertIn(15.3, grid_data[key])

    def test_calculate_view_matrix_afr(self):
        grid_data = {(1, 0): [14.0, 15.0]}
        filters = {'temp': 'ALL', 'tps': 'ALL'}
        target_map = {}

        val_matrix, txt_matrix, _, _, _, _ = self.processor.calculate_view_matrix(
            grid_data, 'afr', filters, target_map
        )

        self.assertEqual(val_matrix[0, 1], 14.5)
        self.assertEqual(txt_matrix[0, 1], "14.5")

    def test_calculate_view_matrix_deviation(self):
        grid_data = {(1, 0): [13.5]}
        filters = {'temp': 'ALL', 'tps': 'ALL'}
        target_map = {(800, 20): 14.7}

        val_matrix, txt_matrix, _, _, _, _ = self.processor.calculate_view_matrix(
            grid_data, 'dev', filters, target_map
        )

        self.assertAlmostEqual(val_matrix[0, 1], -1.2)
        self.assertEqual(txt_matrix[0, 1], "-1.2")


if __name__ == '__main__':
    unittest.main()
