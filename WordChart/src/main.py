import re
import sys
import matplotlib.pyplot as plt
from collections import Counter
from PyQt6.QtCore import Qt
from nltk.corpus import stopwords
import nltk
from PyQt6.QtWidgets import QApplication, QFileDialog, QComboBox, QVBoxLayout, QWidget, QPushButton, QLabel, \
    QSizePolicy, QMenu, QMainWindow
from PyQt6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

try:
    nltk.download('stopwords')
except Exception as e:
    print(f"Error downloading stopwords: {e}")
    sys.exit(1)

class TextAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Word Frequency Analyzer")
        self.setGeometry(300, 300, 800, 600)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FFFFFF, stop: 1 #B2D7D9);
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
        """)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.heading_label = QLabel("Word Frequency Analyzer", self)
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #4C8C6B;
            text-align: center;
            margin-bottom: 20px;
            font-family: 'Segoe UI', sans-serif;
        """)

        self.language_combo = QComboBox(self)
        try:
            languages = load_languages()
            self.language_combo.addItems(languages)
        except Exception as e:
            print(f"Error loading languages: {e}")
            sys.exit(1)
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #F1F1F1;
                border: 1px solid #B2B2B2;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                font-family: Arial;
            }
            QComboBox::drop-down {
                border: none;
                background: #E8E8E8;
            }
            QComboBox::down-arrow {
                image: url('down-arrow.png');
            }
            QComboBox:hover {
                background-color: #D9D9D9;
                border: 1px solid #4C8C6B;
            }
        """)

        self.file_button = QPushButton('Select Text File', self)
        self.file_button.setStyleSheet("""
            QPushButton {
                background-color: #4C8C6B;
                color: white;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #39765B;
                transform: scale(1.05);
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #2F5D4A;
                transform: scale(0.98);
            }
        """)
        self.file_button.clicked.connect(self.select_file)
        self.file_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.status_label = QLabel("Select a language and a text file to analyze.", self)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #555;
            margin-top: 20px;
            text-align: center;
            background-color: #E0E0E0;
            padding: 10px;
            border-radius: 6px;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
        """)

        self.canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
        self.canvas.setStyleSheet("""
            border: 1px solid #B2B2B2;
            border-radius: 10px;
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
        """)

        layout.addWidget(self.heading_label)
        layout.addWidget(self.language_combo)
        layout.addWidget(self.file_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.canvas)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.setLayout(layout)
        self.file_path = None
        self.plot_shown = False

        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = QMenu("File", self)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        save_action.setEnabled(False)

        file_menu.addAction(save_action)
        menu_bar.addMenu(file_menu)
        self.save_action = save_action

    def select_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select a text file", "./", "Text Files (*.txt)")
            if file_path:
                self.file_path = file_path
                self.status_label.setText(f"File loaded: {file_path.split('/')[-1]}")
                self.analyze_text()
            else:
                print("No file selected.")
                self.status_label.setText("No file selected.")
        except Exception as e:
            print(f"Error selecting file: {e}")
            self.status_label.setText(f"Error: {e}")

    def analyze_text(self):
        try:
            language = self.language_combo.currentText()
            stopwords_set = load_stopwords(language)

            words = process_text(self.file_path, stopwords_set)
            word_counts = Counter(words)
            percentages = calc_percentage(word_counts)

            for word, percentage in sorted(percentages.items(), key=lambda x: x[1], reverse=True):
                print(f"{word} - {percentage:.2f}%")

            self.plot_charts(percentages)
            self.status_label.setText(f"Analysis complete. Results shown.")
            self.save_action.setEnabled(True)
        except Exception as e:
            print(f"Error analyzing text: {e}")
            self.status_label.setText(f"Error: {e}")

    def plot_charts(self, percentages):
        try:
            words, values = zip(*sorted(percentages.items(), key=lambda x: x[1], reverse=True)[:10])

            self.canvas.figure.clf()

            ax1 = self.canvas.figure.add_subplot(121)
            explode = [0.1] * len(words)
            colors = plt.cm.viridis(np.linspace(0, 1, len(words)))

            wedges, texts, autotexts = ax1.pie(
                values,
                labels=words,
                autopct='%1.1f%%',
                startangle=140,
                colors=colors,
                explode=explode,
                shadow=True,
                radius=0.9,
                textprops={'fontsize': 8}
            )
            ax1.set_title("Word Frequency Distribution (Top 10)")

            # bar Chart
            ax2 = self.canvas.figure.add_subplot(122)
            ax2.bar(words, values, color='skyblue')
            ax2.set_xlabel("Words")
            ax2.set_ylabel("Percentage (%)")
            ax2.set_title("Word Frequency in Text")
            ax2.set_xticks(range(len(words)))
            ax2.set_xticklabels(words, rotation=45, ha="right")
            ax2.set_ylim(0, max(values) * 1.1)

            self.canvas.draw()

            self.plot_shown = True
        except Exception as e:
            print(f"Error plotting charts: {e}")
            sys.exit(1)

    def save_file(self):
        try:
            if self.plot_shown:
                save_path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "./", "PNG Files (*.png);;JPEG Files (*.jpg)")
                if save_path:
                    self.canvas.print_figure(save_path)
                    print(f"File saved to: {save_path}")
        except Exception as e:
            print(f"Error saving file: {e}")
            self.status_label.setText(f"Error: {e}")

def load_languages(file_path='nltk_languages.txt'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            languages = file.read().splitlines()
        if not languages:
            print("No languages found in the file.")
            sys.exit(1)
        return languages
    except Exception as e:
        print(f"Error reading language file '{file_path}': {e}")
        sys.exit(1)


def load_stopwords(language):
    try:
        return set(stopwords.words(language))
    except Exception as e:
        print(f"Error loading stopwords for language '{language}': {e}")
        sys.exit(1)


def process_text(file_path, stopwords_set):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read().lower()
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        words = [word for word in words if word not in stopwords_set]
        return words
    except FileNotFoundError:
        print(f"Error: the file at {file_path} was not found.")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: Could not decode the file {file_path}. It might not be a text file.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing the file {file_path}: {e}")
        sys.exit(1)


def calc_percentage(word_counts):
    try:
        total_words = sum(word_counts.values())
        percentages = {word: (count / total_words) * 100 for word, count in word_counts.items()}
        return percentages
    except Exception as e:
        print(f"Error calculating percentages: {e}")
        sys.exit(1)


def main():
    app = QApplication(sys.argv)
    window = TextAnalyzerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
