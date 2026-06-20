import cv2
import numpy as np
from PIL import Image, ImageChops, ImageQt
from pyzbar.pyzbar import decode
from PyQt6.QtGui import QImage


def trim_image(image: Image.Image) -> Image.Image:
    """去除 QR Code 圖片的白邊"""
    bg = Image.new(image.mode, image.size, (255, 255, 255))
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    return image.crop(bbox) if bbox else image


def decode_by_cv2(qimage: QImage, detector: cv2.QRCodeDetector) -> tuple[str, str] | None:
    width, height = qimage.width(), qimage.height()
    ptr = qimage.constBits()
    ptr.setsize(qimage.sizeInBytes())
    arr = np.frombuffer(ptr, dtype=np.uint8).reshape(
        (height, width, 4))

    image = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
    image = cv2.copyMakeBorder(image, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    data, _, _ = detector.detectAndDecode(image)
    return (data, "cv2") if data else None


def decode_by_pyzbar(qimage: QImage) -> tuple[str, str] | None:
    text = None
    decoded_image = ImageQt.fromqimage(qimage)
    decoded_objects = decode(decoded_image)
    if decoded_objects:
        
        try:
            text = decoded_objects[0].data.decode('utf-8')
        except UnicodeDecodeError:
            text = decoded_objects[0].data.hex()
    return (text, "pyzbar (Warning: May have encoding issues)") if text else None
