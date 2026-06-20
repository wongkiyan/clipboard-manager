import pyperclip
import ctypes

def run():
    cbm_string = pyperclip.paste()
    swapped_string = cbm_string

    # 🚀 使用 if-elif 結構，確保轉換只會觸發一次，不會被重複覆蓋
    if '\\' in cbm_string:
        swapped_string = cbm_string.replace('\\', '/')
        pyperclip.copy(swapped_string)
    elif '/' in cbm_string:
        swapped_string = cbm_string.replace('/', '\\')
        pyperclip.copy(swapped_string)
    else:
        # 如果根本沒斜線，跳出提示並結束
        ctypes.windll.user32.MessageBoxW(
            0, "提示：未在剪貼簿文字中找到任何斜線（/ 或 \\）。", "Slash Swapper", 48)
        return

    # 🚀 替代原本的 print，改用 Windows 彈出視窗回報結果
    message = f"斜線轉換成功！已複製新路徑。\n\n原本: {cbm_string}\n轉換: {swapped_string}"
    ctypes.windll.user32.MessageBoxW(
        0, message, "Slash Swapper", 64)

if __name__ == "__main__":
    run()
