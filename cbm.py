# TODO: detect slash in txtClipboard
# TODO: Disable button for a second
# TODO: Add New Function: Google image search

from datetime import datetime
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout, QListWidgetItem
from PyQt6.QtCore import QDir, Qt, QTimer, QMimeData, QStandardPaths, QSettings, pyqtSignal, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt6.QtGui import QPixmap
from ui import Ui_Form
import qrcode
from PIL import ImageQt, Image, ImageChops
from pyzbar.pyzbar import decode
import cv2
import numpy as np
import shelve
import configs as Configs
from time import time
import traceback
import sys

QDir.addSearchPath("icons", "images")

# Max size of text for a single QR code, adjust accordingly
MAX_TEXT_LENGTH = 2000  # QR Code version 1 has a max capacity of around 295 characters

IMAGE_PREVIEW_MAX_WIDTH = 300
IMAGE_PREVIEW_MAX_HEIGHT = 300

DISABLE_BUTTON_TIMEOUT = 1000

class NotificationWidget(QWidget):
    # Define a custom signal that emits a message
    notification_signal = pyqtSignal(str)

    def __init__(self, parent=None, timeout=2000):
        super().__init__(parent)

        self.setVisible(False)

        # Create the notification widget
        self.notification_widget = QWidget(self)
        self.notification_widget.setStyleSheet(
            "background-color: lightgreen; padding: 5px; border-radius: 5px;")

        # Layout for the notification (inside the notification widget)
        notification_layout = QHBoxLayout()
        self.message_label = QLabel("QR Code copied to clipboard", self)
        self.close_button = QPushButton("X", self)
        self.close_button.clicked.connect(self.hide_notification)

        notification_layout.addWidget(self.message_label)
        notification_layout.addWidget(self.close_button)
        self.notification_widget.setLayout(notification_layout)

        # Timer for auto-hide
        self.timeout = timeout  # Time in milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_notification)

        # Connect the signal to show_notification
        self.notification_signal.connect(self.show_notification)

    def update_notification_position(self):
        """Update the notification position to the bottom-right corner."""
        parent_width = self.parent().width()  # Get the current parent window width
        parent_height = self.parent().height()  # Get the current parent window height
        # Get the width and height of the notification box
        notification_width = self.width()
        notification_height = self.height()

        # Set the position to the bottom-right corner (with some padding)
        x_pos = parent_width - notification_width - 10  # 10px padding from the right
        y_pos = parent_height - notification_height - 10  # 10px padding from the bottom

        # Set the geometry of the notification widget
        self.move(x_pos, y_pos)

    def show_notification(self, message):
        """Show the notification with an optional custom message."""
        self.message_label.setText(message)
        self.close_button.adjustSize()
        self.notification_widget.adjustSize()
        self.adjustSize()
        self.update_notification_position()
        self.setVisible(True)
        self.timer.start(self.timeout)

    def hide_notification(self):
        """Hide the notification."""
        self.setVisible(False)
        self.timer.stop()

class CustomListItem(QWidget):
    def __init__(self, text, parent_list, notification_signal):
        super().__init__()
        self.parent_list = parent_list  # Reference to the QListWidget
        self.notification_signal = notification_signal

        # Create label to display text
        self.label = QLabel(text)

        # Create remove button
        self.remove_btn = QPushButton("❌")
        self.remove_btn.setFixedSize(30, 30)  # Adjust button size
        self.remove_btn.clicked.connect(self.remove_item)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.remove_btn)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setStretch(0, 1)  # Stretch the label to take available space
        layout.setStretch(1, 0)  # Don't stretch the delete button
        layout.setSpacing(10)
        self.setLayout(layout)

    def remove_item(self):
        shelf = shelve.open(Configs.SHELF_DATA_PATH)
        key_to_remove = None
        value_to_remove = self.label.text()

        for key, value in shelf.items():
            if str(value) == value_to_remove:
                key_to_remove = key
                break

        if key_to_remove:
            del shelf[key_to_remove]

        shelf.close()

        item = self.parent_list.itemAt(self.pos())
        if item:
            row = self.parent_list.row(item)
            self.parent_list.takeItem(row)

        # QMessageBox.information(self, "Item Removed","The selected item has been removed.")
        self.notification_signal.emit("The selected item has been removed.")

class ImageViewer(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Viewer")

        # Layout for the image viewer dialog
        layout = QVBoxLayout()

        # QLabel to show the image
        self.imgLabel = QLabel(self)
        self.imgLabel.setPixmap(image)  # Set the full-size image
        self.imgLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the image label to the layout
        layout.addWidget(self.imgLabel)

        self.setLayout(layout)
        self.resize(image.size())

        # Make the image clickable to close the viewer
        self.imgLabel.mousePressEvent = self.close_image_viewer

    def close_image_viewer(self, event):
        # Close the image viewer dialog when the image is clicked
        self.accept()


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.settings = parent.settings

        layout = QVBoxLayout(self)

        self.ask_reload_checkbox = QCheckBox("Ask before reloading clipboard")
        self.ask_reload_checkbox.setChecked(self.settings.value("reload_confirmation", "ask") == "ask")

        layout.addWidget(self.ask_reload_checkbox)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

    def save_settings(self):
        self.settings.setValue(
            "reload_confirmation", "ask" if self.ask_reload_checkbox.isChecked() else "skip")
        self.accept()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.buttons = {
            "save_data"             : {"button": self.ui.btnSaveData, "on_click": self.save_data},
            "toggle_slash"          : {"button": self.ui.btnToggleSlash, "on_click": self.toggle_slash},
            "convert_qr"            : {"button": self.ui.btnConvertQR, "on_click": self.convert_qrcode},
            "reload_content"        : {"button": self.ui.btnReloadContent, "on_click": self.reload_content},
            "copy_content"          : {"button": self.ui.btnCopyContent, "on_click": self.copy_content},
            "remove_selected_item"  : {"button": self.ui.btnRemoveListItem, "on_click": self.remove_selected_item},
            "copy_selected_item"    : {"button": self.ui.btnCopyListItem, "on_click": self.copy_selected_item},
            "open_settings"         : {"button": self.ui.btnOpenSetting, "on_click": self.open_settings},
        }
        self.setup_buttons()
        self.ui.listWidget.itemDoubleClicked.connect(self.copy_selected_item)

        self.notification_widget = NotificationWidget(self)
        self.notification_signal = self.notification_widget.notification_signal

        self.clipboard = QApplication.clipboard()
        self.detector = cv2.QRCodeDetector()
        self.default_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        self.settings = QSettings("ClipboardManager", "MainApp")

        self.reload_clipboard_content()
        self.reload_list_widget_content()
        self.resize_list_widget()

    def setup_buttons(self):
        for key, value in self.buttons.items():
            btn:QPushButton = value["button"]
            btn.clicked.connect(value["on_click"])
            btn.clicked.connect(self.pulse_animation)
            btn.clicked.connect(self.disable_button_temporarily)

    def reload_clipboard_content(self):
        mime_data = self.clipboard.mimeData()

        if mime_data.hasImage():
            image = self.clipboard.image()
            if image.isNull():
                QMessageBox.warning(self, "Error", "Clipboard image is null!")
                self.ui.txtClipboard.setVisible(True)
                self.ui.imgClipboard.setVisible(False)
                return

            pixmap = QPixmap.fromImage(image)
            if pixmap.isNull():
                QMessageBox.warning(self, "Error", "QPixmap conversion failed!")
                self.ui.txtClipboard.setVisible(True)
                self.ui.imgClipboard.setVisible(False)
                return
            
            self.image = pixmap

            pixmap = pixmap.scaled(IMAGE_PREVIEW_MAX_WIDTH, IMAGE_PREVIEW_MAX_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio)
            self.ui.imgClipboard.setPixmap(pixmap)
            self.ui.imgClipboard.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.imgClipboard.setVisible(True)
            self.ui.imgClipboard.mousePressEvent = self.open_image_viewer
            self.ui.txtClipboard.setVisible(False)
        else:
            clipboard_text = self.clipboard.text()
            self.ui.txtClipboard.setPlainText(clipboard_text)
            self.ui.txtClipboard.setVisible(True)
            self.ui.imgClipboard.setVisible(False)

    def resize_clipboard_content(self):
        self.ui.txtClipboard.setFixedHeight(self.ui.txtClipboard.sizeHint().height())
        self.ui.txtClipboard.setFixedWidth(self.ui.txtClipboard.sizeHint().width())

    def show_notification_message(self, message: str):
        """ Helper function to show notifications easily from anywhere in the app. """
        self.notification_signal.emit(message)

    def open_image_viewer(self, event):
        # When the image is clicked, open the image viewer dialog
        viewer = ImageViewer(self.image, self)
        viewer.exec()  # Show the dialog

    def reload_list_widget_content(self):
        self.ui.listWidget.clear()
        shelf = shelve.open(Configs.SHELF_DATA_PATH)
        self.insert_custom_widget_items(shelf)
        shelf.close()

    def insert_default_widget_items(self, shelf):
        self.ui.listWidget.addItems(map(str, list(shelf.values())))

    def insert_custom_widget_items(self, shelf):
        for value in shelf.values():
            custom_widget = CustomListItem(str(value), self.ui.listWidget, self.notification_signal)
            item = QListWidgetItem(self.ui.listWidget)
            item.setSizeHint(custom_widget.sizeHint())
            self.ui.listWidget.addItem(item)
            self.ui.listWidget.setItemWidget(item, custom_widget)

    def resize_list_widget(self):
        total_height = 0
        max_width = 0

        for index in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(index)

            total_height += item.sizeHint().height()

            item_width = item.sizeHint().width()

            max_width = max(max_width, item_width)

        
        width = min(total_height + 10, 500)
        height = min(max_width + 10, 500)
        current_maximumSize = self.ui.listWidget.maximumSize()

        self.ui.listWidget.setFixedSize(width, height)

        self.adjustSize()
        self.adjustSize()

        self.ui.listWidget.setMaximumSize(current_maximumSize)

    def pulse_animation(self):
        sender = self.sender()  # 獲取觸發此函數的按鈕
        if not isinstance(sender, QPushButton):  # 確保 sender 是按鈕
            return

        # 建立放大動畫
        expand_anim = QPropertyAnimation(sender, b"geometry")
        expand_anim.setDuration(200)
        expand_anim.setStartValue(sender.geometry())
        expanded_rect = sender.geometry().adjusted(-5, -5, 5, 5)  # 放大
        expand_anim.setEndValue(expanded_rect)
        expand_anim.setEasingCurve(QEasingCurve.Type.OutBounce)

        # 建立縮小動畫
        shrink_anim = QPropertyAnimation(sender, b"geometry")
        shrink_anim.setDuration(200)
        shrink_anim.setStartValue(expanded_rect)
        shrink_anim.setEndValue(sender.geometry())  # 回到原本大小
        shrink_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 使用動畫群組串聯動畫
        animation_group = QSequentialAnimationGroup()
        animation_group.addAnimation(expand_anim)
        animation_group.addAnimation(shrink_anim)

        self.anim = animation_group  # 儲存動畫，避免被 GC 回收
        self.anim.start()

    def remove_selected_item(self):
        selected_items = self.ui.listWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection",
                                "Please select an item to remove.")
            return

        selected_item = selected_items[0]

        shelf = shelve.open(Configs.SHELF_DATA_PATH)
        key_to_remove = None
        value_to_remove = None

        custom_widget = self.ui.listWidget.itemWidget(selected_item)  # Retrieve the CustomListItem widget
        if isinstance(custom_widget, CustomListItem):  # Ensure it's a CustomListItem widget
            value_to_remove = custom_widget.label.text()  # Access the label text
        else:
            value_to_remove = selected_item.text()

        if value_to_remove is None:
            QMessageBox.warning(self, "Value Not Found",
                                "The selected item value not found.")
            return

        for key, value in shelf.items():
            if str(value) == value_to_remove:
                key_to_remove = key
                break

        if key_to_remove:
            del shelf[key_to_remove]

        shelf.close()

        self.ui.listWidget.takeItem(self.ui.listWidget.row(selected_item))

        # QMessageBox.information(self, "Item Removed","The selected item has been removed.")
        self.show_notification_message("The selected item has been removed.")

    def copy_selected_item(self):
        selected_items = self.ui.listWidget.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "No Selection","Please select an item to copy.")
            return

        text_to_copy = "\n".join(self.ui.listWidget.itemWidget(item).label.text() for item in selected_items)
        self.clipboard.setText(text_to_copy)
        self.reload_clipboard_content()

        # QMessageBox.information(self, "Copied", "The selected item(s) have been copied.")
        self.show_notification_message("The selected item(s) have been copied.")

    def reload_content(self):
        # Check if user has disabled confirmation
        if self.settings.value("reload_confirmation", "ask") != "skip":
            # Create message box
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Confirm Reload")
            msg_box.setText(
                "Are you sure you want to reload the clipboard content?\n\nThis will override any changes you made in the text box.")
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)

            # Add "Don't ask again" checkbox
            dont_ask_checkbox = QCheckBox("Don't ask again")
            msg_box.setCheckBox(dont_ask_checkbox)

            # Show dialog
            reply = msg_box.exec()

            # Save preference if checked
            if dont_ask_checkbox.isChecked():
                self.settings.setValue("reload_confirmation", "skip")

            if reply == QMessageBox.StandardButton.No:
                return
        self.reload_clipboard_content()
        self.show_notification_message("Content Reloaded from the clipboard.")

    def copy_content(self):
        if self.ui.txtClipboard.isVisible():
            self.clipboard.setText(self.ui.txtClipboard.toPlainText())
            # QMessageBox.information(self, "Text Copied", "Text has been copied to the clipboard")
            self.show_notification_message("Text has been copied to the clipboard.")
        elif self.ui.imgClipboard.isVisible():
            pixmap = self.ui.imgClipboard.pixmap()

            if pixmap:
                image = pixmap.toImage()

                mime_data = QMimeData()
                mime_data.setImageData(image)

                self.clipboard.setMimeData(mime_data)

                # QMessageBox.information(self, "Image Copied", "Image has been copied to the clipboard")
                self.show_notification_message("Image has been copied to the clipboard.")
        else:
            QMessageBox.warning(
                self, "Text or Image Not Found", "No Text / image found!")

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def save_data(self):
        if self.ui.txtClipboard.isVisible():
            clipboard_text = self.ui.txtClipboard.toPlainText()
            shelf = shelve.open(Configs.SHELF_DATA_PATH)
            unique_key = str(int(time()))
            shelf[unique_key] = clipboard_text
            shelf.close()
            self.reload_list_widget_content()
            self.show_notification_message("Text saved successfully!")
        elif self.ui.imgClipboard.isVisible():
            default_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_image"
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Image", f"{self.default_dir}/{default_name}", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)"
            )
            if not file_name:
                QMessageBox.information(self, "Selection Cancelled", "No file was selected.")
                return

            pixmap = self.ui.imgClipboard.pixmap()

            if not pixmap:
                QMessageBox.warning(None, "Pixmap Not Found",
                                    "No Pixmap found in imgClipboard!")
                return

            image = pixmap.toImage()
            image.save(file_name)
            # QMessageBox.information(self, "Success", "Image saved successfully!")
            self.show_notification_message("Image saved successfully!")
        else:
            QMessageBox.warning(None, "Clipboard Is Empty",
                                "Nothing can save.")

    def toggle_slash(self):
        if self.ui.imgClipboard.isVisible():
            QMessageBox.warning(None, "Clipboard Contains Image",
                                "The clipboard contains an image.")

        elif self.ui.txtClipboard.isVisible():
            clipboard_text = self.ui.txtClipboard.toPlainText()

            if '\\' in clipboard_text:
                clipboard_text = clipboard_text.replace('\\', '/')
            elif '/' in clipboard_text:
                clipboard_text = clipboard_text.replace('/', '\\')
            else:
                # QMessageBox.information(None, "No Slash Found", "No slashes were found in the clipboard text.")
                self.show_notification_message("No slashes were found in the clipboard text.")
                return

            self.clipboard.setText(clipboard_text)
            self.ui.txtClipboard.setPlainText(clipboard_text)
            # QMessageBox.information(None, "Slash Toggled", "The result has been copied to the clipboard.")
            self.show_notification_message("The result has been copied to the clipboard.")

    def convert_qrcode(self):
        try:
            if self.ui.imgClipboard.isVisible():
                # Get the pixmap from the QLabel
                pixmap = self.ui.imgClipboard.pixmap()

                if pixmap.isNull():
                    QMessageBox.warning(None, "Pixmap Not Found",
                                        "No Pixmap found in imgClipboard!")
                    return None

                # Convert QPixmap to QImage
                qimage = pixmap.toImage()

                decode_result = self.decode_by_cv2(qimage) or self.decode_by_pyzbar(qimage)
                
                if decode_result is None:
                    QMessageBox.warning(self, "No QR Code",
                                        "No QR Code found in the image!")
                    return
                decoded_text, decoder_used = decode_result
                self.clipboard.setText(decoded_text)
                self.reload_clipboard_content()
                # QMessageBox.information(self, "QR Code Detected", f"Result has been copied\nDecoded using: {decoder_used}")
                self.show_notification_message(f"Result has been copied\nDecoded using: {decoder_used}")
            elif self.ui.txtClipboard.isVisible():
                text = self.ui.txtClipboard.toPlainText()
                if text == "":
                    QMessageBox.warning(self, "Empty Text","Nothing in text box.")
                    return
                try:
                    # Check if the text is too long
                    if len(text) > MAX_TEXT_LENGTH:
                        # Ask the user if they want to split the text
                        reply = QMessageBox.question(self, "Text Too Long",
                                    f"The text is too long to fit into a single QR code. Would you like to split it into multiple QR codes?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                        if reply == QMessageBox.StandardButton.Yes:
                            # Split the text into chunks
                            chunks = [text[i:i + MAX_TEXT_LENGTH]
                                    for i in range(0, len(text), MAX_TEXT_LENGTH)]

                            # Generate QR codes for each chunk
                            for i, chunk in enumerate(chunks):
                                # Create QR code for each chunk
                                qr = qrcode.make(chunk.encode(
                                    'utf-8')).convert("RGB")
                                qr_trimmed = self.trim_image(qr)
                                qr_qimage = ImageQt.toqimage(qr_trimmed)
                                self.clipboard.setImage(qr_qimage)
                                self.reload_clipboard_content()
                                QMessageBox.information(
                                    self, f"QR Code {i + 1}", f"QR Code {i + 1} generated and copied to clipboard!")

                            QMessageBox.information(
                                self, "Done", "All QR codes have been generated.")
                        else:
                            QMessageBox.warning(self, "Operation Cancelled",
                                                "No QR code was generated.")
                    else:
                        # If text is small enough, generate a single QR code
                        qr = qrcode.make(text.encode('utf-8')).convert("RGB")
                        qr_trimmed = self.trim_image(qr)
                        qr_qimage = ImageQt.toqimage(qr_trimmed)
                        self.clipboard.setImage(qr_qimage)
                        self.reload_clipboard_content()
                        # QMessageBox.information(self, "QR Code Generated", "QR Code copied to clipboard!")
                        self.show_notification_message("QR Code copied to clipboard!")

                except ValueError as e:
                    if "expected 1 to 40" in str(e):
                        QMessageBox.warning(
                            self, "Text too long", f"Failed to generate QR Code! Please shorten it to fit the limit.")
                    else:
                        QMessageBox.warning(
                            self, "Error", f"Failed to generate QR Code: {str(e)}")
            else:
                QMessageBox.warning(self, "Clipboard Empty",
                                    "Clipboard does not contain text or an image!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"{str(e)}")

    def decode_by_cv2(self, qimage)-> tuple[str, str] | None:
        width, height = qimage.width(), qimage.height()

        # Convert QImage to byte array
        ptr = qimage.constBits()
        ptr.setsize(qimage.sizeInBytes())  # Ensure correct size
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape(
            (height, width, 4))  # ARGB format

        # Convert ARGB to BGR (OpenCV uses BGR)
        image = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
        # Add border to image else not detectable for a qr code only image
        image = cv2.copyMakeBorder(image, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[255, 255, 255])

        data, _, _ = self.detector.detectAndDecode(image)

        return (data,"cv2") if data else None

    def decode_by_pyzbar(self, qimage) -> tuple[str, str] | None:
        text = None
        decoded_image = ImageQt.fromqimage(qimage)
        decoded_objects = decode(decoded_image)
        if decoded_objects:
            try:
                text = decoded_objects[0].data.decode('utf-8')  # 嘗試 UTF-8 解碼
            except UnicodeDecodeError:
                text = decoded_objects[0].data.hex()  # 以 16 進制顯示原始數據，避免報錯

        return (text, "pyzbar (Warning: May have encoding issues)") if text else None

    def disable_button_temporarily(self):
        sender = self.sender()
        if not isinstance(sender, QPushButton):
            return
        sender.setEnabled(False)
        QTimer.singleShot(DISABLE_BUTTON_TIMEOUT, lambda: sender.setEnabled(True))

    def trim_image(self, image: Image.Image) -> Image.Image:
        """去除 QR Code 圖片的白邊"""
        bg = Image.new(image.mode, image.size, (255, 255, 255))  # 創建純白背景
        diff = ImageChops.difference(image, bg)  # 計算 QR Code 與背景的差異
        bbox = diff.getbbox()  # 取得非白色區域的邊界
        return image.crop(bbox) if bbox else image  # 裁剪圖片

def main():
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())  # Start the Qt event loop
    except Exception as e:
        print("An error occurred:", e)
        print(traceback.format_exc())  # Print full traceback


if __name__ == "__main__":
    main()