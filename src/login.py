from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import socket
from database_config import SERVER_HOST, SERVER_PORT

class LoginWindow(QWidget):
    def __init__(self, on_login_success, show_register_window):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(400, 300)
        self.on_login_success = on_login_success
        self.show_register_window = show_register_window

        self.title = QLabel("Login to Your Account")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Arial", 18, QFont.Bold))

        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Username")

        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Password")
        self.password_entry.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_user)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.show_register_window)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        self.setLayout(layout)

    def login_user(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((SERVER_HOST, SERVER_PORT))
                command = f"LOGIN {username} {password}"
                client_socket.sendall(command.encode())
                response = client_socket.recv(1024).decode()

                if response == "Login successful":
                    QMessageBox.information(self, "Success", "Login successful!")
                    self.on_login_success(username)
                else:
                    QMessageBox.warning(self, "Error", "Invalid username or password.")
        except Exception as e:
            QMessageBox.warning(self, "Connection Error", f"Could not connect to server: {e}")
