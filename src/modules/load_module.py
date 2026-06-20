import pyperclip, shelve, sys
from src import configs
import ctypes

def run():
    # 防禦機制：防止使用者沒帶 Key 導致 sys.argv[2] 噴出 IndexError
    if len(sys.argv) < 3:
        ctypes.windll.user32.MessageBoxW(
            # 16 是紅色叉叉
            0, "錯誤：未指定要載入的 Key 參數。\n範例：cbm load [Key]", "Clipboard Manager - Error", 16)
        return

    key = sys.argv[2]
    cbm_shelf = shelve.open(configs.SHELF_DATA_PATH)

    if key in cbm_shelf:
        value = str(cbm_shelf[key])
        pyperclip.copy(value)

        # 🚀 彈出視窗顯示成功複製的詳細內容
        message = f"成功載入並複製到剪貼簿！\n\nKey: {key}\nValue: {value}"
        ctypes.windll.user32.MessageBoxW(
            0, message, "Clipboard Manager - Load", 64)
    else:
        # 如果找不到該 Key，跳出錯誤警告
        ctypes.windll.user32.MessageBoxW(
            0, f"錯誤：找不到指定的 Key「{key}」", "Clipboard Manager - Error", 16)

    cbm_shelf.close()

if __name__ == "__main__":
    run()