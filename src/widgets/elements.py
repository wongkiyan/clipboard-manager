
import shelve
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer, pyqtSignal
from src import configs

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
        shelf = shelve.open(configs.SHELF_DATA_PATH)
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
