import pyperclip
import ctypes

def run():
    cbm_string = pyperclip.paste()

    # 檢查剪貼簿是否為空
    if not cbm_string:
        ctypes.windll.user32.MessageBoxW(
            0, "提示：目前的剪貼簿是空的。", "Slash Swapper", 48)
        return

    # 檢查有沒有任何斜線
    if '/' not in cbm_string and '\\' not in cbm_string:
        ctypes.windll.user32.MessageBoxW(
            0, "提示：未在剪貼簿文字中找到任何斜線（/ 或 \\）。", "Slash Swapper", 48)
        return

    # 進行斜線變換
    swap_table = str.maketrans({'/': '\\', '\\': '/'})
    swapped_string = cbm_string.translate(swap_table)
    pyperclip.copy(swapped_string)

    # 彈出視窗顯示轉換前後的結果
    message = f"斜線轉換成功！已複製新路徑。\n\n原本: {cbm_string}\n轉換: {swapped_string}"
    ctypes.windll.user32.MessageBoxW(
        0, message, "Slash Swapper", 64)

if __name__ == "__main__":
    run()