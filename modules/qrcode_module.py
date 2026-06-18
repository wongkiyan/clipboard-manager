import pyperclip
from PIL import ImageGrab
from pyzbar.pyzbar import decode

def run():
    # Get image data from clipboard
    image_data = ImageGrab.grabclipboard()

    # Check if image data is available
    if image_data is None:
        print("No image data found in the clipboard.")
        return

    # Convert clipboard data to Pillow Image
    img = image_data

    # Decode QR code
    decoded_objects = decode(img)
    print("-- QR code operation executed --")

    # If QR code is found, get the text
    if decoded_objects:
        qr_text = decoded_objects[0].data.decode('utf-8')
        # Copy text to clipboard
        pyperclip.copy(qr_text)
        print("QR code text copied to clipboard:", qr_text)
    else:
        print("No QR code found in the image.")


if __name__ == "__main__":
    run()
