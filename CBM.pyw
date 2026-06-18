# cbm.pyw - Clipboard manager.
# Usage: 
#       cbm save <keyword> - Saves clipboard to keyword
#       cbm <keyword> - Loads keyword to clipboard
#       cbm ls - Loads all keywords to clipboard

import sys, os
import configs as Configs
from modules import save_module
from modules import load_module
from modules import list_module
from modules import clear_module
from modules import slash_module
from modules import qrcode_module
from cbm import main

request_functions = {
    "SAVE" : save_module.run,
    "LOAD" : load_module.run,
    "LIST" : list_module.run,
    "CLEAR" : clear_module.run,
    "SLASH" : slash_module.run,
    "QRCODE": qrcode_module.run,
}

def handle_request():
    if not os.path.exists(Configs.PROGRAM_DATA_PATH):
        os.makedirs(Configs.PROGRAM_DATA_PATH)
        print("!!! Please run the setup.bat for the initial usage. !!!")

    if len(sys.argv) == 1:
        main()

    if len(sys.argv) >= 2:
        request_type = sys.argv[1].upper()
        function_to_execute = request_functions.get(request_type)
        function_to_execute() if function_to_execute else print("Request type not found: {request_type}. Exiting.")
        return

    print("Usage: cbm <request_type> [additional_arguments]")

if __name__ == "__main__":
    handle_request()