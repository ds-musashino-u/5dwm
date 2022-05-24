import math
import colorsys
import numpy as np
from PIL import Image

MULT_FCTR = 40
DIV_FCTR = 8


def resize_image(image, max_image_length=512):
    width, height = image.size

    if width > height:
        if width > max_image_length:
            image = image.resize((max_image_length, round(
                max_image_length / width * height)), Image.Resampling.BILINEAR)

    elif height > max_image_length:
        image = image.resize((round(max_image_length / height * width),
                             max_image_length), Image.Resampling.BILINEAR)

    return image


def compute_histogram(rgb_image, r=0.1, r1=0.85, normalize=None):
    histogram = np.zeros(round(2 * math.pi * MULT_FCTR) +
                         1 + round(255.0 / DIV_FCTR) + 1, dtype=np.float64)

    for y in range(rgb_image.shape[0]):
        for x in range(rgb_image.shape[1]):
            r, g, b = rgb_image[y, x]
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            h *= 2 * math.pi
            v *= 255.0

            wh = 0.0 if v == 0.0 else math.pow(s, r * math.pow(255.0 / v, r1))
            wi = 1.0 - wh

            histogram[round(h * MULT_FCTR)] += wh
            histogram[round(2 * math.pi * MULT_FCTR) + round(v / DIV_FCTR)] += wi
            #histogram[round(2 * math.pi * MULT_FCTR) + 1 + round(v / DIV_FCTR)] += wi

    if normalize is None:
        histogram /= rgb_image.shape[0] * rgb_image.shape[1]
    elif normalize == 'chuan_hoa':
        histogram = histogram / np.sum(histogram) * 100

    return histogram


def top_k(data, k):
    top_k = []

    for i in range(data.shape[0]):
        top_k.append((i, data[i]))

    top_k.sort(key=lambda x: x[1])
    top_k.reverse()

    return top_k[:k]
