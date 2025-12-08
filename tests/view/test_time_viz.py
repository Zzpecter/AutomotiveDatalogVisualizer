import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication
from datalog_visualizer.view.tabs.timeseries_viz_tab import TimeSeriesVizTab

app = QApplication([])


class TestTimeAnalysisTab(unittest.TestCase):
    def setUp(self):
        self.mock_main_window = MagicMock()
        self.mock_main_window.df = pd.DataFrame()
        self.tab = TimeSeriesVizTab(self.mock_main_window)

        self.tab.x_data = np.array([0, 1, 2, 3, 4, 5])
        self.tab.df = pd.DataFrame({
            'Time': self.tab.x_data,
            'RPM': [1000, 2000, 3000, 4000, 5000, 6000],
            'TPS': [0, 10, 20, 50, 100, 100],
            'ConstVal': [5, 5, 5, 5, 5, 5]
        })

        self.tab.sensor_config = {
            "RPM": {
                "data_type": "int",
                "category": "engine",
                "importance": 1,
                "range": [0, 0],
                "alerts": [
                    {
                        "type": "WARNING",
                        "condition": "gt",
                        "value": 2000.0
                    },
                    {
                        "type": "CRITICAL",
                        "condition": "gt",
                        "value": 5000.0
                    }
                ]
            },
            "TPS": {
                "data_type": "int",
                "category": "engine",
                "importance": 1,
                "range": [0, 0],
                "alerts": []
            }
        }

    def test_refresh_data_source_filtering(self):
        self.tab.main_window.df = self.tab.df
        self.tab.refresh_data_source()
        items = []
        for i in range(self.tab.sensor_list.count()):
            items.append(self.tab.sensor_list.item(i).text())

        self.assertIn('RPM', items)
        self.assertIn('TPS', items)
        self.assertNotIn('ConstVal', items)
        self.assertNotIn('Time', items)

    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    @patch('pandas.DataFrame.to_csv')
    def test_save_trim_logic(self, mock_to_csv, mock_file_dialog):
        self.tab.spin_trim_start.setValue(1.0)
        self.tab.spin_trim_end.setValue(3.0)
        mock_file_dialog.return_value = ('test_save_trim_logic.csv', 'CSV Files (*.csv)')
        self.tab.save_trim()

        self.assertTrue(mock_to_csv.called)
        args, _ = mock_to_csv.call_args
        saved_df = args[0]

        self.assertEqual(saved_df, 'test_save_trim_logic.csv')

    def test_alert_detection_critical(self):
        mock_btn = MagicMock()
        mock_btn.text.return_value = "CRITICAL"
        self.tab.bg_alerts.checkedButton = MagicMock(return_value=mock_btn)
        self.tab.plot_curves = {'RPM': MagicMock()}
        self.tab.plot_widget.addItem = MagicMock()
        self.tab.refresh_alerts()

        self.assertTrue(self.tab.plot_widget.addItem.called)
        scatter_item = self.tab.alert_scatter

        self.assertIsNotNone(scatter_item)
        self.assertEqual(len(scatter_item.data), 1)
        self.assertEqual(scatter_item.data[0]['x'], 5.0)

    def test_alert_detection_none(self):
        mock_btn = MagicMock()
        mock_btn.text.return_value = "NONE"
        self.tab.bg_alerts.checkedButton = MagicMock(return_value=mock_btn)
        self.tab.plot_curves = {'RPM': MagicMock()}
        self.tab.plot_widget.addItem = MagicMock()
        self.tab.refresh_alerts()

        self.assertFalse(self.tab.plot_widget.addItem.called)
        self.assertIsNone(self.tab.alert_scatter)

    def test_zoom_calculation(self):
        self.tab.slider_zoom.setValue(50)
        self.tab.plot_widget.setXRange = MagicMock()
        self.tab.apply_zoom()

        self.tab.plot_widget.setXRange.assert_called_with(1.25, 3.75, padding=0)


if __name__ == '__main__':
    unittest.main()
