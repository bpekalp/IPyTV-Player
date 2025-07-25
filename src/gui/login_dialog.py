"""
Login Dialog for IPTV Player
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
    QLabel,
    QGroupBox,
)
from PyQt6.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to IPTV Server")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Create group box
        group_box = QGroupBox("Xtream Codes Credentials")
        form_layout = QFormLayout(group_box)

        # Server URL input
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("http://your-server.com:8080")
        form_layout.addRow("Server URL:", self.server_input)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("username")
        form_layout.addRow("Username:", self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("password")
        form_layout.addRow("Password:", self.password_input)

        layout.addWidget(group_box)

        # Add info label
        info_label = QLabel("Enter your Xtream Codes server credentials to connect")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info_label)

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set focus to server input
        self.server_input.setFocus()

        # Connect Enter key to accept
        self.server_input.returnPressed.connect(self.username_input.setFocus)
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.accept)

    def get_credentials(self):
        return {
            "server": self.server_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text().strip(),
        }

    def accept(self):
        # Validate inputs
        credentials = self.get_credentials()
        if not all(credentials.values()):
            return  # Don't accept if any field is empty

        super().accept()
