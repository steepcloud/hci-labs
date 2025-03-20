import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit, \
    QLabel, QFileDialog
import re


class TextProcessor:
    @staticmethod
    def anonymize_names(text):
        try:
            import nltk
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            try:
                nltk.data.find('corpora/names')
            except LookupError:
                nltk.download('names')

            from nltk.corpus import names as nltk_names
            name_list = set(nltk_names.words())
        except ImportError:
            # fallback to simple name list
            name_list = {"John", "Michael", "David", "James", "Robert", "William", "Mary",
                         "Jennifer", "Linda", "Elizabeth", "Susan", "Patricia", "Sarah"}

        sentences = re.split(r'(?<=[.!?])\s+', text)
        processed_sentences = []

        for sentence in sentences:
            words = sentence.split()
            if not words:
                processed_sentences.append(sentence)
                continue

            processed_words = []

            for i, word in enumerate(words):
                clean_word = re.sub(r'[^\w]', '', word)

                if clean_word and clean_word[0].isupper() and clean_word in name_list:
                    match = re.match(r'([A-Z][a-zA-Z]*)(.*)', word)
                    if match:
                        name_part, rest = match.groups()
                        processed_words.append("xxx" + rest)
                    else:
                        processed_words.append(word)

                elif i == 0 and clean_word and clean_word[0].isupper():
                    if clean_word in name_list:
                        match = re.match(r'([A-Z][a-zA-Z]*)(.*)', word)
                        if match:
                            name_part, rest = match.groups()
                            processed_words.append("xxx" + rest)
                        else:
                            processed_words.append(word)
                    else:
                        processed_words.append(word)

                elif clean_word and clean_word[0].isupper() and i > 0:
                    match = re.match(r'([A-Z][a-zA-Z]*)(.*)', word)
                    if match:
                        name_part, rest = match.groups()
                        processed_words.append("xxx" + rest)
                    else:
                        processed_words.append(word)
                else:
                    processed_words.append(word)

            processed_sentences.append(' '.join(processed_words))

        return ' '.join(processed_sentences)


class NameAnonymizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text_processor = TextProcessor()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Name Anonymizer')
        self.setGeometry(100, 100, 800, 600)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #c0c0c0;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
        """)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        input_label = QLabel("Input Text:")
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter text containing names to anonymize...")

        button_layout = QHBoxLayout()

        self.anonymize_button = QPushButton("Anonymize Names")
        self.anonymize_button.clicked.connect(self.anonymize_text)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_texts)

        self.load_button = QPushButton("Load File")
        self.load_button.clicked.connect(self.load_file)

        self.save_button = QPushButton("Save Output")
        self.save_button.clicked.connect(self.save_output)

        button_layout.addWidget(self.anonymize_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)

        output_label = QLabel("Anonymized Text:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Anonymized text will appear here...")

        main_layout.addWidget(input_label)
        main_layout.addWidget(self.input_text)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(output_label)
        main_layout.addWidget(self.output_text)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def anonymize_text(self):
        input_text = self.input_text.toPlainText()
        if input_text:
            anonymized_text = self.text_processor.anonymize_names(input_text)
            self.output_text.setPlainText(anonymized_text)

    def clear_texts(self):
        self.input_text.clear()
        self.output_text.clear()

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    self.input_text.setPlainText(text)
            except Exception as e:
                self.output_text.setPlainText(f"Error loading file: {str(e)}")

    def save_output(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Output", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.output_text.toPlainText())
            except Exception as e:
                self.output_text.setPlainText(f"Error saving file: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = NameAnonymizerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()