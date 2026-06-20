import os

# Max size of text for a single QR code, adjust accordingly
MAX_TEXT_LENGTH = 2000  # QR Code version 1 has a max capacity of around 295 characters

IMAGE_PREVIEW_MAX_WIDTH = 300
IMAGE_PREVIEW_MAX_HEIGHT = 300

DISABLE_BUTTON_TIMEOUT = 1000

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
PROGRAM_DATA_PATH = os.path.join(PROJECT_ROOT, "data")
SHELF_DATA_PATH = os.path.join(PROGRAM_DATA_PATH, "cbm")

if not os.path.exists(PROGRAM_DATA_PATH):
    os.makedirs(PROGRAM_DATA_PATH)