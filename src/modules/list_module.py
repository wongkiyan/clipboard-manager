import shelve
from src import configs
import ctypes

def run():
    cbm_shelf = shelve.open(configs.SHELF_DATA_PATH)
    keys = list(cbm_shelf.keys())
    cbm_shelf.close()

    # 🚀 將所有 Key 組合成多行文字，直接用視窗彈出來看
    if keys:
        message = "目前的歷史紀錄 Key 列表：\n\n" + "\n".join(map(str, keys))
    else:
        message = "目前資料庫中沒有任何紀錄。"

    ctypes.windll.user32.MessageBoxW(
        0, message, "Clipboard Manager - List", 64)

if __name__ == "__main__":
    run()