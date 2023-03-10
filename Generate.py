import argparse
import os
import cv2


parser = argparse.ArgumentParser(description='Data Generator')
parser.add_argument('--fonts', help='Path to fonts folder.', required=True)
parser.add_argument('--out', help='Path to out folder.', required=True)
parser.add_argument('--size', help='Size of the images.', nargs=2, default=[40, 40], type=int)
parser.add_argument('--count', help='Number of files for single char in a single font.', type=int, default=50)
args = parser.parse_args()

if args.fonts:
    import imgaug.augmenters as iaa
    import imutils
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont


def square(img):
    assert type(img) == np.ndarray
    d, r = divmod(abs(img.shape[0] - img.shape[1]), 2)
    if img.shape[0] > img.shape[1]:
        return cv2.copyMakeBorder(img, 0, 0, d if not r else d + 1, d, cv2.BORDER_CONSTANT, 0)
    else:
        return cv2.copyMakeBorder(img, d if not r else d + 1, d, 0, 0, cv2.BORDER_CONSTANT, 0)


def generate_images(fontSize, imageSize, dataPath, dataSize, fontFiles):
    alphabet = {
        "a": "أ", "b": "ب", "t": "ت", "th": "ث", "g": "ج", "hh": "ح",
        "kh": "خ", "d": "د", "the": "ذ", "r": "ر", "z": "ز", "c": "س",
        "sh": "ش", "s": "ص", "dd": "ض", "tt": "ط", "zz": "ظ", "i": "ع",
        "gh": "غ", "f": "ف", "q": "ق", "k": "ك", "l": "ل", "m": "م",
        "n": "ن", "h": "ه", "w": "و", "y": "ي", "0": "٠", "1": "١", "2": "٢",
        "3": "٣", "4": "٤", "5": "٥", "6": "٦", "7": "٧", "8": "٨", "9": "٩"
    }

    seq = iaa.Sequential([
        iaa.Sometimes(0.6, iaa.Crop(percent=(0, 0.4))),
        iaa.Sometimes(0.6, iaa.Affine(
            scale={"x": (0.8, 1.2), "y": (0.8, 1.2)},
            rotate=(-20, 20)
        ))], random_order=True)

    for idx, (key, value) in enumerate(alphabet.items()):
        os.makedirs("{}/{}".format(dataPath, idx), exist_ok=True)
        for i, path in enumerate(fontFiles):
            img = np.zeros(tuple(map(sum, zip(imageSize, (50, 50)))), np.uint8)
            font = ImageFont.truetype((args.fonts + '/' + path), fontSize)
            img_pil = Image.fromarray(img)
            draw = ImageDraw.Draw(img_pil)
            draw.text((20, -15), value, font=font, fill=255)
            img = [np.array(img_pil) for _ in range(dataSize)]

            for idx2, value2 in enumerate(img):
                kernel = np.ones((3, 3), dtype=np.uint8)
                thresh = cv2.dilate(value2, kernel, iterations=3)
                cns = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cns = imutils.grab_contours(cns)
                (x, y, w, h) = cv2.boundingRect(cns[0])
                image = value2[y:y + h, x:x + w]
                image = square(image)
                image = cv2.resize(image, imageSize)
                image = seq.augment_image(image)
                cv2.imwrite("{}/{}/{}.jpg".format(dataPath, idx, (idx2 + (dataSize * i))), image)


if os.path.exists(args.fonts):
    fonts = os.listdir(args.fonts)
    generate_images(50, tuple(args.size), args.out, args.count, fonts)
