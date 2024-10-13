import colorsys
import numpy as np
from PIL import Image, ImageOps

MULT_FCTR = 40
DIV_FCTR = 8


def resize_image(image, max_image_length=512):
    image = ImageOps.exif_transpose(image)
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
    histogram = np.zeros(round(2 * np.pi * MULT_FCTR) +
                         1 + round(255.0 / DIV_FCTR) + 1, dtype=np.float64)

    for y in range(rgb_image.shape[0]):
        for x in range(rgb_image.shape[1]):
            red, green, blue = rgb_image[y, x]
            hue, saturation, value = colorsys.rgb_to_hsv(red / 255.0, green / 255.0, blue / 255.0)
            hue *= 2 * np.pi
            value *= 255.0

            wh = 0.0 if value == 0.0 else np.power(saturation, r * np.power(255.0 / value, r1))
            wi = 1.0 - wh

            histogram[round(hue * MULT_FCTR)] += wh
            histogram[round(2 * np.pi * MULT_FCTR) + round(value / DIV_FCTR)] += wi
            # Paper code
            # histogram[round(2 * np.pi * MULT_FCTR) + 1 + round(value / DIV_FCTR)] += wi

    if normalize == 'l1':
        histogram = histogram / np.sum(histogram)
    elif normalize == 'l2':
        histogram = histogram / np.sqrt(np.sum(histogram * histogram))

    return histogram


def top_k(data, k):
    top_k = []

    for i in range(data.shape[0]):
        top_k.append((i, data[i]))

    top_k.sort(key=lambda x: x[1])
    top_k.reverse()

    return top_k[:k]
