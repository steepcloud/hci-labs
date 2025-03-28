import sys
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QTextEdit, QPushButton,
                             QFrame, QMessageBox, QListWidget)
from PyQt6.QtCore import Qt, QTimer


class EmailExtractorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Extractor")
        self.setMinimumSize(550, 570)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(25)
        self.main_layout.setContentsMargins(35, 35, 35, 35)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        title_label = QLabel("✉️ Email Extractor")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label)

        desc_label = QLabel("Enter text containing email addresses to extract them")
        desc_label.setObjectName("descLabel")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(desc_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("separator")
        self.main_layout.addWidget(separator)

        input_layout = QVBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text with email addresses, e.g. Contact us at john@doe.com or support@doe.com")
        self.text_input.setObjectName("textInput")
        input_layout.addWidget(self.text_input)

        extract_btn = QPushButton("Extract Email Addresses")
        extract_btn.setObjectName("extractBtn")
        extract_btn.clicked.connect(self.extract_emails)
        input_layout.addWidget(extract_btn)

        self.main_layout.addLayout(input_layout)

        results_frame = QFrame()
        results_frame.setObjectName("resultsFrame")
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(20)

        results_title = QLabel("Extracted Email Addresses")
        results_title.setObjectName("resultsTitle")
        results_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.addWidget(results_title)

        self.emails_list = QListWidget()
        self.emails_list.setObjectName("emailsList")
        results_layout.addWidget(self.emails_list)

        self.main_layout.addWidget(results_frame)
        self.main_layout.addStretch()

    def extract_emails(self):
        text = self.text_input.toPlainText().strip()

        if not text:
            self.show_error("Please enter text containing email addresses.")
            return

        email_pattern = r'([a-zA-Z]+)@([a-zA-Z]+)\.[a-zA-Z]+'
        emails = re.findall(email_pattern, text)

        if not emails:
            self.show_error("No valid email addresses found.")
            return

        self.emails_list.clear()

        for username, domain in emails:
            email = f"{username}@{domain}.com"
            list_item = f"Email: {email} | Username: {username} | Company: {domain}"
            self.emails_list.addItem(list_item)

        self.highlight_results()

    def show_error(self, message):
        QMessageBox.warning(self, "Input Error", message)

    def highlight_results(self):
        self.emails_list.setStyleSheet("background-color: rgba(104, 211, 145, 0.4); border-radius: 4px;")
        QTimer.singleShot(1000, self.reset_highlight)

    def reset_highlight(self):
        self.emails_list.setStyleSheet("")
        self.emails_list.style().unpolish(self.emails_list)
        self.emails_list.style().polish(self.emails_list)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f4f8;
            }

            #titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2a4365;
                margin-bottom: 10px;
                padding: 10px;
            }

            #descLabel {
                font-size: 15px;
                color: #4a5568;
                margin-bottom: 15px;
            }

            #separator {
                color: #cbd5e0;
                height: 2px;
            }

            #textInput {
                padding: 12px;
                border: 1px solid #a0aec0;
                border-radius: 6px;
                font-size: 14px;
                background-color: #ffffff;
                min-height: 100px;
            }

            #textInput:focus {
                border: 1px solid #4299e1;
                box-shadow: 0 0 5px rgba(66, 153, 225, 0.5);
            }

            #extractBtn {
                padding: 12px;
                background-color: #4299e1;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
            }

            #extractBtn:hover {
                background-color: #3182ce;
            }

            #extractBtn:pressed {
                background-color: #2b6cb0;
            }

            #resultsFrame {
                background-color: white;
                border-radius: 10px;
                padding: 25px;
                margin-top: 25px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }

            #resultsTitle {
                font-size: 18px;
                font-weight: bold;
                color: #2d3748;
                margin-bottom: 10px;
            }

            #emailsList {
                font-size: 14px;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 5px;
                background-color: #f8fafc;
            }

            #emailsList::item {
                padding: 8px;
                border-bottom: 1px solid #e2e8f0;
            }

            #emailsList::item:selected {
                background-color: #3182ce;
                color: white;
            }

            #emailsList::item:last {
                border-bottom: none;
            }

            #emailsList::item:hover {
                background-color: #ebf8ff;
            }

            #emailsList::item:hover:selected {
                background-color: #2c5282;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmailExtractorApp()
    window.show()
    sys.exit(app.exec())