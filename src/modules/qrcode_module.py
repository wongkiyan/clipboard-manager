import pyperclip
import ctypes
from PIL import ImageGrab
from pyzbar.pyzbar import decode


def run():
    # 從剪貼簿取得圖片資料
    image_data = ImageGrab.grabclipboard()

    # 檢查剪貼簿內是否有圖片
    if image_data is None:
        ctypes.windll.user32.MessageBoxW(
            0, "錯誤：剪貼簿內沒有偵測到圖片資料！", "QR Code Reader", 16)  # 16 是紅色叉叉
        return

    # 解碼 QR Code
    decoded_objects = decode(image_data)

    # 如果找到 QR Code，取得文字內容
    if decoded_objects:
        qr_text = decoded_objects[0].data.decode('utf-8')
        # 複製文字到剪貼簿
        pyperclip.copy(qr_text)

        message = f"成功辨識 QR Code 並已複製到剪貼簿！\n\n內容：\n{qr_text}"
        ctypes.windll.user32.MessageBoxW(
            0, message, "QR Code Reader", 64)  # 64 是藍色資訊圖示
    else:
        ctypes.windll.user32.MessageBoxW(
            0, "提示：這張圖片中沒有找到任何可辨識的 QR Code。", "QR Code Reader", 48)  # 48 是黃色驚嘆號


if __name__ == "__main__":
    run()