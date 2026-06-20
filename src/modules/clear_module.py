import shelve
from src import configs
import ctypes

def run():
    cbm_shelf = shelve.open(configs.SHELF_DATA_PATH)
    cbm_shelf.clear()
    cbm_shelf.close()
    ctypes.windll.user32.MessageBoxW(0, "All saved keywords have been cleared.", "Clear Operation", 64)

if __name__ == "__main__":
    run()