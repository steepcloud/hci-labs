import sys
import random
import string
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QSpinBox,
                             QLineEdit, QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon


class PasswordGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Generator")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: #2c3e50; color: #ecf0f1;")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        header_label = QLabel("Secure Password Generator")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #3498db; margin: 10px;")
        main_layout.addWidget(header_label)

        desc_label = QLabel("Generate random passwords with specific character requirements")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("font-style: italic; margin-bottom: 20px;")
        main_layout.addWidget(desc_label)

        length_group = QGroupBox("Password Configuration")
        length_group.setStyleSheet(
            "QGroupBox { border: 1px solid #3498db; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        length_layout = QVBoxLayout(length_group)

        pattern_label = QLabel("Default pattern: 3 digits + 3 punctuation + 3 uppercase + 3 lowercase")
        pattern_label.setStyleSheet("color: #f39c12;")
        length_layout.addWidget(pattern_label)

        custom_length_checkbox = QCheckBox("Use custom length instead of default pattern")
        custom_length_checkbox.setStyleSheet("margin-top: 10px;")
        length_layout.addWidget(custom_length_checkbox)

        length_widget = QWidget()
        length_box = QHBoxLayout(length_widget)
        length_label = QLabel("Password Length:")
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 32)
        self.length_spin.setValue(12)
        self.length_spin.setEnabled(False)
        self.length_spin.setStyleSheet(
            "background-color: #34495e; border: 1px solid #3498db; border-radius: 3px; padding: 5px;")
        length_box.addWidget(length_label)
        length_box.addWidget(self.length_spin)
        length_layout.addWidget(length_widget)

        self.char_options = QWidget()
        char_layout = QVBoxLayout(self.char_options)

        self.use_digits = QCheckBox("Include digits (0-9)")
        self.use_digits.setChecked(True)
        self.use_punctuation = QCheckBox("Include punctuation (!@#$%^&*...)")
        self.use_punctuation.setChecked(True)
        self.use_uppercase = QCheckBox("Include uppercase letters (A-Z)")
        self.use_uppercase.setChecked(True)
        self.use_lowercase = QCheckBox("Include lowercase letters (a-z)")
        self.use_lowercase.setChecked(True)

        char_layout.addWidget(self.use_digits)
        char_layout.addWidget(self.use_punctuation)
        char_layout.addWidget(self.use_uppercase)
        char_layout.addWidget(self.use_lowercase)

        self.char_options.setEnabled(False)
        length_layout.addWidget(self.char_options)

        main_layout.addWidget(length_group)

        custom_length_checkbox.toggled.connect(self.toggle_custom_mode)

        result_group = QGroupBox("Generated Password")
        result_group.setStyleSheet(
            "QGroupBox { border: 1px solid #3498db; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        result_layout = QVBoxLayout(result_group)

        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setStyleSheet(
            "background-color: #34495e; border: 1px solid #3498db; border-radius: 3px; padding: 8px; font-family: monospace; font-size: 14px; color: #2ecc71;")
        self.password_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.password_display)

        main_layout.addWidget(result_group)

        button_layout = QHBoxLayout()

        generate_btn = QPushButton("Generate Password")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        generate_btn.clicked.connect(self.generate_password)

        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        copy_btn.clicked.connect(self.copy_to_clipboard)

        button_layout.addWidget(generate_btn)
        button_layout.addWidget(copy_btn)
        main_layout.addLayout(button_layout)

        self.generate_password()

    def toggle_custom_mode(self, checked):
        self.length_spin.setEnabled(checked)
        self.char_options.setEnabled(checked)

    def generate_password(self):
        if self.length_spin.isEnabled():
            length = self.length_spin.value()
            chars = ""
            if self.use_digits.isChecked():
                chars += string.digits
            if self.use_punctuation.isChecked():
                chars += string.punctuation
            if self.use_uppercase.isChecked():
                chars += string.ascii_uppercase
            if self.use_lowercase.isChecked():
                chars += string.ascii_lowercase

            if not chars:
                self.password_display.setText("Error: Select at least one character type!")
                return

            password = ''.join(random.choice(chars) for _ in range(length))
        else:
            digits = ''.join(random.choice(string.digits) for _ in range(3))
            punctuation = ''.join(random.choice(string.punctuation) for _ in range(3))
            uppercase = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
            lowercase = ''.join(random.choice(string.ascii_lowercase) for _ in range(3))

            password = digits + punctuation + uppercase + lowercase

        self.password_display.setText(password)

    def copy_to_clipboard(self):
        if self.password_display.text():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.password_display.text())
            self.statusBar().showMessage("Password copied to clipboard!", 2000)


def main():
    app = QApplication(sys.argv)
    window = PasswordGenerator()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()