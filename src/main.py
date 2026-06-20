from src.modules import (
    save_module,
    load_module,
    list_module,
    clear_module,
    slash_module,
    qrcode_module
)
import sys
import os
from src import configs
import ctypes

# 延遲引入 GUI，只有在真正需要時才載入 PyQt6，加快 CLI 指令的反應速度
def start_gui():
    from src.gui_app import launch_gui
    launch_gui()


request_functions = {
    "SAVE": save_module.run,
    "LOAD": load_module.run,
    "LIST": list_module.run,
    "CLEAR": clear_module.run,
    "SLASH": slash_module.run,
    "QRCODE": qrcode_module.run,
}

def show_windows_popup(title, message):
    """使用 Windows 原生彈出視窗回報訊息"""
    # 64 代表資訊圖示 (Information Icon)
    ctypes.windll.user32.MessageBoxW(0, message, title, 64)

def handle_request():
    # 狀況 A：沒有帶任何參數 -> 啟動 PyQt6 視窗
    if len(sys.argv) == 1:
        start_gui()
        return

    # 狀況 B：有帶參數 -> 走命令列（CLI）捷徑
    if len(sys.argv) >= 2:
        request_type = sys.argv[1].upper()
        function_to_execute = request_functions.get(request_type)

        if function_to_execute:
            function_to_execute()
        else:
            show_windows_popup("Error", f"Request type not found: {request_type}. Exiting.")
        return


if __name__ == "__main__":
    handle_request()