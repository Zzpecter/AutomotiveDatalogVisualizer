import unittest
from datalog_visualizer.config.constants import X_TICKS, Y_TICKS


class TestConfig(unittest.TestCase):
    def test_ticks_validity(self):
        self.assertIsInstance(X_TICKS, list)
        self.assertIsInstance(Y_TICKS, list)
        self.assertTrue(len(X_TICKS) > 0)
        self.assertTrue(len(Y_TICKS) > 0)

        self.assertEqual(X_TICKS, sorted(X_TICKS))
        self.assertEqual(Y_TICKS, sorted(Y_TICKS))


if __name__ == '__main__':
    unittest.main()
