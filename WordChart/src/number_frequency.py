import matplotlib.patheffects as path_effects
import sys
import pandas as pd
import matplotlib.cm as cm
from matplotlib.figure import Figure
from collections import Counter
import numpy as np
import seaborn as sns
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QFileDialog, QVBoxLayout, QWidget,
                             QPushButton, QLabel, QSizePolicy, QMenu, QMainWindow,
                             QTabWidget, QComboBox, QHBoxLayout, QGridLayout)
from PyQt6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class NumberAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Number Frequency Analyzer")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #2C3E50, stop: 1 #3498DB);
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.1);
            }
            QTabBar::tab {
                background-color: #34495e;
                color: white;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
            }
            QTabBar::tab:hover {
                background-color: #2980b9;
            }
        """)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        header_layout = QHBoxLayout()
        self.heading_label = QLabel("Number Frequency Analyzer", self)
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #ECF0F1;
            text-align: center;
            margin: 20px 0;
            font-family: 'Segoe UI', sans-serif;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        """)
        header_layout.addWidget(self.heading_label)
        main_layout.addLayout(header_layout)

        control_panel = QWidget()
        control_panel.setStyleSheet("""
            background-color: rgba(52, 73, 94, 0.7);
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
        """)
        control_layout = QGridLayout(control_panel)

        self.file_button = QPushButton('Select CSV File', self)
        self.file_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)
        self.file_button.clicked.connect(self.select_file)
        self.file_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.column_combo = QComboBox()
        self.column_combo.setStyleSheet("""
            QComboBox {
                background-color: #2C3E50;
                border: 1px solid #1ABC9C;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox:hover {
                background-color: #34495E;
                border: 1px solid #2ECC71;
            }
            QComboBox::drop-down {
                border: none;
                background: #1ABC9C;
                width: 30px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        self.column_combo.currentIndexChanged.connect(self.analyze_data)

        column_label = QLabel("Select Column:")
        column_label.setStyleSheet("color: #ECF0F1; font-weight: bold;")

        self.display_combo = QComboBox()
        self.display_combo.addItems(["Top 10", "Top 20", "Top 50", "All"])
        self.display_combo.setStyleSheet("""
            QComboBox {
                background-color: #2C3E50;
                border: 1px solid #1ABC9C;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox:hover {
                background-color: #34495E;
                border: 1px solid #2ECC71;
            }
            QComboBox::drop-down {
                border: none;
                background: #1ABC9C;
                width: 30px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        self.display_combo.currentIndexChanged.connect(self.analyze_data)

        display_label = QLabel("Display Count:")
        display_label.setStyleSheet("color: #ECF0F1; font-weight: bold;")

        control_layout.addWidget(self.file_button, 0, 0, 1, 2)
        control_layout.addWidget(column_label, 1, 0)
        control_layout.addWidget(self.column_combo, 1, 1)
        control_layout.addWidget(display_label, 2, 0)
        control_layout.addWidget(self.display_combo, 2, 1)

        main_layout.addWidget(control_panel)

        self.status_label = QLabel("Select a CSV file to analyze.", self)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #ECF0F1;
            text-align: center;
            background-color: rgba(41, 128, 185, 0.3);
            padding: 10px;
            border-radius: 6px;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
            margin-bottom: 10px;
        """)
        main_layout.addWidget(self.status_label)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: rgba(44, 62, 80, 0.7);
                border-radius: 10px;
            }
        """)

        self.basic_tab = QWidget()
        self.advanced_tab = QWidget()
        self.distribution_tab = QWidget()

        self.tabs.addTab(self.basic_tab, "Basic Charts")
        self.tabs.addTab(self.advanced_tab, "Advanced Charts")
        self.tabs.addTab(self.distribution_tab, "Distribution Analysis")

        basic_layout = QVBoxLayout(self.basic_tab)
        advanced_layout = QVBoxLayout(self.advanced_tab)
        distribution_layout = QVBoxLayout(self.distribution_tab)

        self.basic_canvas = FigureCanvas(Figure(figsize=(10, 6)))
        self.advanced_canvas = FigureCanvas(Figure(figsize=(10, 6)))
        self.distribution_canvas = FigureCanvas(Figure(figsize=(10, 6)))

        basic_layout.addWidget(self.basic_canvas)
        advanced_layout.addWidget(self.advanced_canvas)
        distribution_layout.addWidget(self.distribution_canvas)

        main_layout.addWidget(self.tabs)

        self.create_menu_bar()

        self.file_path = None
        self.data = None
        self.numeric_columns = []
        self.frequency_data = {}

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #2C3E50;
                color: white;
                border-bottom: 1px solid #1ABC9C;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 15px;
            }
            QMenuBar::item:selected {
                background-color: #1ABC9C;
            }
            QMenu {
                background-color: #2C3E50;
                color: white;
                border: 1px solid #1ABC9C;
            }
            QMenu::item:selected {
                background-color: #1ABC9C;
            }
        """)

        file_menu = QMenu("File", self)

        save_action = QAction("Save Charts", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_charts)
        save_action.setEnabled(False)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        menu_bar.addMenu(file_menu)
        self.save_action = save_action

    def select_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select a CSV file", "./", "CSV Files (*.csv)")
            if file_path:
                self.file_path = file_path
                self.status_label.setText(f"Loading file: {file_path.split('/')[-1]}")
                self.load_data()
            else:
                self.status_label.setText("No file selected.")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def load_data(self):
        try:
            self.data = pd.read_csv(self.file_path)
            self.numeric_columns = self.data.select_dtypes(include=[np.number]).columns.tolist()

            if not self.numeric_columns:
                self.status_label.setText("No numeric columns found in the CSV file.")
                return

            self.column_combo.clear()
            self.column_combo.addItems(self.numeric_columns)

            self.status_label.setText(f"File loaded: {self.file_path.split('/')[-1]}. Select a column to analyze.")
            self.save_action.setEnabled(True)

            self.analyze_data()

        except Exception as e:
            self.status_label.setText(f"Error loading data: {e}")

    def analyze_data(self):
        if not self.data is not None or not self.numeric_columns:
            return

        try:
            if self.column_combo.currentText() == "":
                return

            column_name = self.column_combo.currentText()
            numbers = self.data[column_name].dropna().values

            counter = Counter(numbers)

            display_option = self.display_combo.currentText()
            if display_option == "Top 10":
                n_items = 10
            elif display_option == "Top 20":
                n_items = 20
            elif display_option == "Top 50":
                n_items = 50
            else:
                n_items = len(counter)

            sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:n_items]
            values, counts = zip(*sorted_items) if sorted_items else ([], [])

            self.frequency_data = {
                'values': values,
                'counts': counts,
                'column': column_name,
                'n_items': n_items
            }

            self.update_plots()
            self.status_label.setText(f"Analyzing column '{column_name}'. Showing top {n_items} frequent numbers.")

        except Exception as e:
            self.status_label.setText(f"Error analyzing data: {e}")

    def update_plots(self):
        if not self.frequency_data:
            return

        try:
            values = self.frequency_data['values']
            counts = self.frequency_data['counts']
            column = self.frequency_data['column']

            self.update_basic_charts(values, counts, column)
            self.update_advanced_charts(values, counts, column)
            self.update_distribution_charts(column)

        except Exception as e:
            self.status_label.setText(f"Error updating plots: {e}")

    def update_basic_charts(self, values, counts, column):
        try:
            fig = self.basic_canvas.figure
            fig.clear()

            colors = cm.viridis(np.linspace(0, 1, len(values)))

            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)

            bars = ax1.bar(range(len(values)), counts, color=colors)
            ax1.set_xticks(range(len(values)))
            ax1.set_xticklabels([str(v) for v in values], rotation=45, ha='right')
            ax1.set_title(f'Frequency of Numbers in {column}', fontsize=14)
            ax1.set_xlabel('Number', fontsize=12)
            ax1.set_ylabel('Frequency', fontsize=12)

            for bar in bars:
                height = bar.get_height()
                ax1.annotate(f'{height}',
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3),
                             textcoords="offset points",
                             ha='center', va='bottom',
                             fontsize=8, color='white')

            total = sum(counts)
            explode = [0.03] * len(values)

            wedges, texts, autotexts = ax2.pie(
                counts,
                labels=[str(v) for v in values],
                autopct=lambda pct: f'{pct:.1f}%',
                startangle=90,
                colors=colors,
                explode=explode,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1}
            )

            for text in texts:
                text.set_fontsize(9)
                text.set_color('black')
                text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])

            for autotext in autotexts:
                autotext.set_fontsize(8)
                autotext.set_color('black')
                autotext.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
                autotext.set_fontweight('bold')

            labels = [f"{v} ({c}, {c / total * 100:.1f}%)" for v, c in zip(values, counts)]
            ax2.legend(wedges, labels,
                       title="Number (Count, %)",
                       loc="center left",
                       bbox_to_anchor=(1, 0, 0.5, 1),
                       fontsize=8)

            ax2.set_title(f'Number Distribution in {column}', fontsize=14)

            fig.tight_layout()
            self.basic_canvas.draw()

        except Exception as e:
            self.status_label.setText(f"Error updating basic charts: {e}")

    def update_advanced_charts(self, values, counts, column):
        try:
            fig = self.advanced_canvas.figure
            fig.clear()

            ax1 = fig.add_subplot(121)

            sorted_indices = np.argsort(counts)
            sorted_values = [values[i] for i in sorted_indices]
            sorted_counts = [counts[i] for i in sorted_indices]

            colors = cm.plasma(np.linspace(0, 1, len(sorted_values)))

            bars = ax1.barh(range(len(sorted_values)), sorted_counts, color=colors)
            ax1.set_yticks(range(len(sorted_values)))
            ax1.set_yticklabels([str(v) for v in sorted_values])
            ax1.set_title('Sorted Frequency Distribution', fontsize=14)
            ax1.set_xlabel('Frequency', fontsize=12)
            ax1.set_ylabel('Number', fontsize=12)

            for bar in bars:
                width = bar.get_width()
                ax1.annotate(f'{width}',
                             xy=(width, bar.get_y() + bar.get_height() / 2),
                             xytext=(5, 0),
                             textcoords="offset points",
                             ha='left', va='center',
                             fontsize=8, color='white')

            ax2 = fig.add_subplot(122)
            sizes = np.array(counts) * 100

            n = len(values)
            cols = int(np.ceil(np.sqrt(n)))
            rows = int(np.ceil(n / cols))

            x_coords = []
            y_coords = []
            for i in range(n):
                row = i // cols
                col = i % cols
                x_coords.append(col)
                y_coords.append(rows - row - 1)

            scatter = ax2.scatter(x_coords, y_coords, s=sizes, c=colors, alpha=0.7)

            for i, (x, y, val) in enumerate(zip(x_coords, y_coords, values)):
                text = ax2.annotate(str(val),
                                    xy=(x, y),
                                    ha='center', va='center',
                                    fontsize=9, color='black',
                                    fontweight='bold')
                text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])

            ax2.set_title('Bubble Chart of Frequencies', fontsize=14)
            ax2.set_xticks([])
            ax2.set_yticks([])
            ax2.set_aspect('equal')

            fig.tight_layout()
            self.advanced_canvas.draw()

        except Exception as e:
            self.status_label.setText(f"Error updating advanced charts: {e}")

    def update_distribution_charts(self, column):
        try:
            fig = self.distribution_canvas.figure
            fig.clear()

            data = self.data[column].dropna()

            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)

            sns.histplot(data, kde=True, ax=ax1, color='skyblue', edgecolor='black')
            ax1.set_title(f'Distribution of {column}', fontsize=14)
            ax1.set_xlabel(column, fontsize=12)
            ax1.set_ylabel('Frequency', fontsize=12)

            sns.boxplot(y=data, ax=ax2, color='lightgreen')
            ax2.set_title(f'Box Plot of {column}', fontsize=14)
            ax2.set_ylabel(column, fontsize=12)

            stats_text = (
                f"Mean: {data.mean():.2f}\n"
                f"Median: {data.median():.2f}\n"
                f"Std Dev: {data.std():.2f}\n"
                f"Min: {data.min():.2f}\n"
                f"Max: {data.max():.2f}\n"
                f"Count: {data.count()}"
            )

            ax2.text(1.05, 0.5, stats_text,
                     transform=ax2.transAxes,
                     fontsize=10,
                     verticalalignment='center',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

            fig.tight_layout()
            self.distribution_canvas.draw()

        except Exception as e:
            self.status_label.setText(f"Error updating distribution charts: {e}")

    def save_charts(self):
        try:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Charts", "./",
                                                       "PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)")
            if not save_path:
                return

            tabs = {
                0: (self.basic_canvas, "basic_charts"),
                1: (self.advanced_canvas, "advanced_charts"),
                2: (self.distribution_canvas, "distribution_charts")
            }

            if '.' not in save_path:
                save_path = f"{save_path}.png"

            base_path = save_path.rsplit('.', 1)[0]
            extension = save_path.rsplit('.', 1)[1]

            for tab_idx, (canvas, name) in tabs.items():
                path = f"{base_path}_{name}.{extension}"
                canvas.figure.savefig(path, bbox_inches='tight', dpi=300)

            self.status_label.setText(f"Charts saved successfully to {base_path}_*.{extension}")
        except Exception as e:
            self.status_label.setText(f"Error saving charts: {e}")

def main():
    app = QApplication(sys.argv)
    window = NumberAnalyzerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()