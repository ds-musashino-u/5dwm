import unittest
import numpy as np
from api.shared.imaging import top_k

MULT_FCTR = 40.0
DIV_FCTR = 8.0


class TestSearch(unittest.TestCase):
    def test_top_k(self):
        self.assertEqual(len(top_k(np.zeros(round(
            2 * np.pi * MULT_FCTR) + 1 + round(255.0 / DIV_FCTR) + 1, dtype=np.float64), 10)), 10)


if __name__ == "__main__":
    unittest.main()
