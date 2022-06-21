import re
import unittest
import numpy as np
from io import BytesIO
from base64 import b64decode
from PIL import Image
from shared.imaging import resize_image, compute_histogram, top_k

MULT_FCTR = 40.0
DIV_FCTR = 8.0


class TestSearch(unittest.TestCase):
    def test_resize_image(self):
        match = re.match("data:([\\w/\\-\\.]+);(\\w+),(.+)", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")

        if match:
            mime_type, encoding, data = match.groups()
            resized_image = resize_image(Image.open(BytesIO(b64decode(data))), 4)

            self.assertEqual(resized_image.width, 4)
            self.assertEqual(resized_image.height, 4)

    def test_compute_histogram(self):
        match = re.match("data:([\\w/\\-\\.]+);(\\w+),(.+)", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")

        if match:
            mime_type, encoding, data = match.groups()
            histogram = compute_histogram(np.array(Image.open(BytesIO(b64decode(data))).convert('RGB')), normalize='l1')
            
            self.assertEqual(len(histogram), round(2 * np.pi * MULT_FCTR) + 1 + round(255.0 / DIV_FCTR) + 1)
            
    def test_top_k(self):
        self.assertEqual(len(top_k(np.zeros(round(
            2 * np.pi * MULT_FCTR) + 1 + round(255.0 / DIV_FCTR) + 1, dtype=np.float64), 10)), 10)


if __name__ == "__main__":
    unittest.main()
