import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDir
from src.widgets.main_window import MainWindow

def launch_gui():
    """
    啟動 PyQt6 圖形使用者介面（GUI）的入口函式。
    只有在 main.py 判斷沒有命令列參數時，才會被呼叫並載入。
    """
    # 設定圖示資源的搜尋路徑（對應你原本 cbm.py 的設定）
    QDir.addSearchPath("icons", "images")
    
    # 建立 PyQt 應用程式實體
    app = QApplication(sys.argv)
    
    try:
        # 初始化並顯示主視窗
        window = MainWindow()
        window.show()
        
        # 進入 PyQt 主事件循環
        sys.exit(app.exec())
        
    except Exception as e:
        print("--- GUI 啟動或執行過程中發生錯誤 ---")
        print(f"錯誤訊息: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    # 如果有人不小心直接執行了這個檔案，它依然能單獨啟動 GUI 方便測試
    launch_gui()