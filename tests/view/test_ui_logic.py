import unittest
from PyQt5.QtWidgets import QApplication
from datalog_visualizer.view.tabs.target_map_tab import TargetMapTab
from datalog_visualizer.view.tabs.danger_cfg_tab import DangerCfgTab
from datalog_visualizer.view.main_window import MainWindow
from PyQt5.QtCore import Qt

app = QApplication([])


class TestUILogic(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()

    def test_color_cell_interpolation(self):
        tab = TargetMapTab(self.window)

        c_ideal = tab._color_cell(13.62)
        self.assertEqual(c_ideal.red(), 255)
        self.assertEqual(c_ideal.green(), 128)
        self.assertEqual(c_ideal.blue(), 0)

        c_lean = tab._color_cell(18.0)
        self.assertEqual(c_lean.red(), 0)
        self.assertEqual(c_lean.green(), 0)

        c_rich = tab._color_cell(5.0)
        self.assertEqual(c_rich.blue(), 255)

        c_mid = tab._color_cell(9.0)
        self.assertGreater(c_mid.blue(), 0)
        self.assertGreater(c_mid.green(), 0)

    def test_danger_input_parsing(self):
        tab = DangerCfgTab(self.window)

        tab.combo_type.setCurrentIndex(tab.combo_type.findText("WARNING", Qt.MatchExactly))
        tab.combo_condition.setCurrentIndex(tab.combo_condition.findText("EQUAL", Qt.MatchExactly))
        tab.inp_value.setText("100")

        data = tab.get_input_data()

        self.assertEqual(data['type'], "WARNING")
        self.assertEqual(data['condition'], "eq")
        self.assertEqual(data['value'], 100)


if __name__ == '__main__':
    unittest.main()
