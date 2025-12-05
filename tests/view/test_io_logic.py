import unittest
from unittest.mock import patch, mock_open
from PyQt5.QtWidgets import QApplication
from datalog_visualizer.view.main_window import MainWindow
app = QApplication([])


class TestIOLogic(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()

    @patch("builtins.open", new_callable=mock_open, read_data='{"800,20": 13.5}')
    @patch("json.load")
    def test_load_target_map_success(self, mock_json_load, mock_file):
        mock_json_load.return_value = {"800,20": 13.5}
        result_map = self.window.load_target_map_from_file()

        self.assertTrue(mock_file.called)
        self.assertIn((800, 20), result_map)
        self.assertEqual(result_map[(800, 20)], 13.5)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_target_map(self, mock_json_dump, mock_file):
        map_data = {(800, 20): 14.2}
        success = self.window.save_target_map_to_file(map_data)

        self.assertTrue(success)
        expected_dump = {"800,20": 14.2}
        mock_json_dump.assert_called_with(expected_dump, mock_file(), indent=4)


if __name__ == '__main__':
    unittest.main()
