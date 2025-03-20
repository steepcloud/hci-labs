from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Standard calculator")
        self.setGeometry(100, 100, 350, 500)
        self.current_expression = ""
        self.error_state = False
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e1e1e, stop:1 #3a3a3a);"
        )
        layout = QVBoxLayout()
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet(
            "background-color: #222; color: white; font-size: 28px; border: none; padding: 10px;"
        )
        layout.addWidget(self.display)

        grid_layout = QGridLayout()
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('C', 4, 0), ('0', 4, 1), ('←', 4, 2), ('+', 4, 3),
            ('(', 5, 0), (')', 5, 1), ('=', 5, 2)
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            button.setFont(QFont("Arial", 18))

            tooltips = {
                '+': "Addition",
                '-': "Subtraction",
                '*': "Multiplication",
                '/': "Division",
                '=': "Evaluate the expression",
                'C': "Clear the display",
                '←': "Delete last character"
            }

            if text in tooltips:
                button.setToolTip(tooltips[text])

            if text in ('+', '-', '*', '/', '(', ')', 'C', '←'):
                button.setStyleSheet(
                    "QPushButton { background-color: #6b6b6b; color: white; border-radius: 5px; padding: 15px; }"
                    "QPushButton:hover { background-color: #888; }"
                    "QPushButton:pressed { background-color: #aaa; }"
                )
            elif text in ('='):
                button.setStyleSheet(
                    "QPushButton { background-color: #a3c2bf; color: white; border-radius: 5px; padding: 15px; }"
                    "QPushButton:hover { background-color: #86adaa; }"
                    "QPushButton:pressed { background-color: #aaa; }"
                )
            else:
                button.setStyleSheet(
                    "QPushButton { background-color: #444; color: white; border-radius: 5px; padding: 15px; }"
                    "QPushButton:hover { background-color: #666; }"
                    "QPushButton:pressed { background-color: #888; }"
                )
            button.clicked.connect(lambda checked, t=text: self.on_button_click(t))
            grid_layout.addWidget(button, row, col)

        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def on_button_click(self, char):
        if self.error_state:
            self.current_expression = ""
            self.error_state = False

        if char == 'C':
            self.current_expression = ""
        elif char == '←':
            self.current_expression = self.current_expression[:-1] if self.current_expression else ""
        elif char == '=':
            self.evaluate_expression()
        else:
            self.current_expression += char

        self.display.setText(self.current_expression)

    def evaluate_expression(self):
        try:
            result = eval(self.current_expression, {"__builtins__": None})
            self.current_expression = str(result)
        except ZeroDivisionError:
            self.current_expression = "Cannot divide by zero"
            self.error_state = True
        except Exception:
            self.current_expression = "Result is undefined"
            self.error_state = True

        self.display.setText(self.current_expression)


if __name__ == "__main__":
    app = QApplication([])
    calculator = Calculator()
    calculator.show()
    app.exec()
