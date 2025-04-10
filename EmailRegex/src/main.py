import sys
import re
import json
import os
import smtplib
from email.message import EmailMessage
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QTextEdit, QPushButton, QHBoxLayout,
                             QFrame, QMessageBox, QListWidget, QDialog,
                             QLineEdit, QDialogButtonBox, QFileDialog)
from PyQt6.QtCore import Qt, QTimer


class EmailSenderDialog(QDialog):
    def __init__(self, recipient, parent=None):
        super().__init__(parent)
        self.recipient = recipient
        self.setWindowTitle("Send Email")
        self.setMinimumSize(500, 500)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"To: {recipient}"))

        layout.addWidget(QLabel("Subject:"))
        self.subject_input = QLineEdit()
        layout.addWidget(self.subject_input)

        layout.addWidget(QLabel("Message:"))
        self.message_input = QTextEdit()
        layout.addWidget(self.message_input)

        layout.addWidget(QLabel("SMTP Server:"))
        self.smtp_server = QLineEdit("smtp.gmail.com")
        layout.addWidget(self.smtp_server)

        layout.addWidget(QLabel("SMTP Port:"))
        self.smtp_port = QLineEdit("587")
        layout.addWidget(self.smtp_port)

        layout.addWidget(QLabel("Email:"))
        self.email = QLineEdit()
        layout.addWidget(self.email)

        layout.addWidget(QLabel("Password:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


class EmailExtractorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Extractor")
        self.setMinimumSize(550, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.contacts_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.json")
        self.saved_contacts = set()
        self.load_contacts()

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
        input_layout.setSpacing(5)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Enter text with email addresses, e.g. Contact us at john@doe.com or support@doe.com")
        self.text_input.setObjectName("textInput")
        self.text_input.setMaximumHeight(100)
        input_layout.addWidget(self.text_input)

        extract_btn = QPushButton("Extract Email Addresses")
        extract_btn.setObjectName("extractBtn")
        extract_btn.clicked.connect(self.extract_emails)
        input_layout.addWidget(extract_btn)

        self.main_layout.addLayout(input_layout)

        results_frame = QFrame()
        results_frame.setObjectName("resultsFrame")
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(10)

        results_title = QLabel("Extracted Email Addresses")
        results_title.setObjectName("resultsTitle")
        results_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.addWidget(results_title)

        self.emails_list = QListWidget()
        self.emails_list.setObjectName("emailsList")
        results_layout.addWidget(self.emails_list)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(5)

        self.save_btn = QPushButton("Save to Contacts")
        self.save_btn.setObjectName("actionBtn")
        self.save_btn.clicked.connect(self.save_to_contacts)
        actions_layout.addWidget(self.save_btn)

        self.send_email_btn = QPushButton("Send Email")
        self.send_email_btn.setObjectName("actionBtn")
        self.send_email_btn.clicked.connect(self.send_email)
        actions_layout.addWidget(self.send_email_btn)

        self.export_btn = QPushButton("Export Contacts")
        self.export_btn.setObjectName("actionBtn")
        self.export_btn.clicked.connect(self.export_contacts)
        actions_layout.addWidget(self.export_btn)

        results_layout.addLayout(actions_layout)

        self.main_layout.addWidget(results_frame)
        self.main_layout.addStretch()

    def extract_emails(self):
        text = self.text_input.toPlainText().strip()

        if not text:
            self.show_error("Please enter text containing email addresses.")
            return

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        emails = re.findall(email_pattern, text)

        if not emails:
            self.show_error("No valid email addresses found.")
            return

        self.emails_list.clear()

        for email in self.saved_contacts:
            username, domain = email.split('@')
            domain_name = domain.split('.')[0]
            list_item = f"Email: {email} | Username: {username} | Company: {domain_name} [Saved]"
            self.emails_list.addItem(list_item)

        for email in emails:
            if email not in self.saved_contacts:
                username, domain = email.split('@')
                domain_name = domain.split('.')[0]
                list_item = f"Email: {email} | Username: {username} | Company: {domain_name}"
                self.emails_list.addItem(list_item)

        self.highlight_results()

    def load_contacts(self):
        if os.path.exists(self.contacts_file):
            try:
                with open(self.contacts_file, 'r') as f:
                    self.saved_contacts = set(json.load(f))
            except Exception as e:
                print(f"Error loading contacts: {e}")
                self.saved_contacts = set()

    def save_to_contacts(self):
        selected_items = self.emails_list.selectedItems()
        if not selected_items:
            self.show_error("Please select emails to save.")
            return

        for item in selected_items:
            text = item.text()
            email_match = re.search(r'Email: ([^\s|]+)', text)
            if email_match:
                email = email_match.group(1)
                self.saved_contacts.add(email)

        try:
            with open(self.contacts_file, 'w') as f:
                json.dump(list(self.saved_contacts), f)
            QMessageBox.information(self, "Success", "Contacts saved successfully!")
        except Exception as e:
            self.show_error(f"Error saving contacts: {e}")

    def send_email(self):
        selected_items = self.emails_list.selectedItems()
        if not selected_items:
            self.show_error("Please select an email recipient.")
            return

        text = selected_items[0].text()
        email_match = re.search(r'Email: ([^\s|]+)', text)
        if not email_match:
            self.show_error("Invalid email selection.")
            return

        recipient = email_match.group(1)
        dialog = EmailSenderDialog(recipient, self)

        if dialog.exec():
            try:
                msg = EmailMessage()
                msg['Subject'] = dialog.subject_input.text()
                msg['From'] = dialog.email.text()
                msg['To'] = recipient
                msg.set_content(dialog.message_input.toPlainText())

                server = smtplib.SMTP(dialog.smtp_server.text(), int(dialog.smtp_port.text()))
                server.starttls()
                server.login(dialog.email.text(), dialog.password.text())
                server.send_message(msg)
                server.quit()

                QMessageBox.information(self, "Success", "Email sent successfully!")
            except Exception as e:
                self.show_error(f"Error sending email: {e}")

    def export_contacts(self):
        if not self.saved_contacts:
            self.show_error("No contacts to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Export Contacts", "", "CSV Files (*.csv);;Text Files (*.txt)")

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    for email in self.saved_contacts:
                        f.write(f"{email}\n")
                QMessageBox.information(self, "Success", f"Contacts exported to {file_path}")
            except Exception as e:
                self.show_error(f"Error exporting contacts: {e}")

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
                font-size: 22px;
                font-weight: bold;
                color: #2a4365;
                padding: 5px;
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
                padding: 8px;
                border: 1px solid #a0aec0;
                border-radius: 4px;
                font-size: 13px;
                background-color: #ffffff;
                min-height: 100px;
            }

            #textInput:focus {
                border: 1px solid #4299e1;
                box-shadow: 0 0 5px rgba(66, 153, 225, 0.5);
            }

            #extractBtn, #actionBtn {
                padding: 6px 10px;
                background-color: #4299e1;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }

            #extractBtn:hover, #actionBtn:hover {
                background-color: #3182ce;
            }

            #extractBtn:pressed, #actionBtn:pressed {
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
                font-size: 16px;
                font-weight: bold;
                color: #2d3748;
            }

            #emailsList {
                font-size: 13px;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 3px;
                background-color: #f8fafc;
            }

            #emailsList::item {
                padding: 5px;
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
