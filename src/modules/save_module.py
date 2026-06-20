import pyperclip
import shelve
import sys
import ctypes
from src import configs


def run():
    # 防禦機制：防止使用者沒帶 Key 參數
    if len(sys.argv) < 3:
        ctypes.windll.user32.MessageBoxW(
            0, "錯誤：未指定要儲存的 Key 名稱。\n範例：cbm save [Key]", "Clipboard Manager - Save Error", 16)
        return

    key = sys.argv[2]
    current_clipboard = pyperclip.paste()

    # 防禦機制：如果剪貼簿目前是空的文字
    if not current_clipboard:
        ctypes.windll.user32.MessageBoxW(
            0, "提示：目前的剪貼簿沒有文字內容，取消儲存。", "Clipboard Manager", 48)
        return

    cbm_shelf = shelve.open(configs.SHELF_DATA_PATH)
    cbm_shelf[key] = current_clipboard
    cbm_shelf.close()

    # 彈出視窗顯示成功
    message = f"成功將剪貼簿文字儲存至資料庫！\n\nKey : {key}\nValue: {current_clipboard}"
    ctypes.windll.user32.MessageBoxW(
        0, message, "Clipboard Manager - Save", 64)


if __name__ == "__main__":
    run()