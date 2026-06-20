from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton
from PyQt6.QtCore import Qt

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
        self.ask_reload_checkbox.setChecked(
            self.settings.value("reload_confirmation", "ask") == "ask")

        layout.addWidget(self.ask_reload_checkbox)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

    def save_settings(self):
        self.settings.setValue(
            "reload_confirmation", "ask" if self.ask_reload_checkbox.isChecked() else "skip")
        self.accept()
