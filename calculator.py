import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QPushButton, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


STYLE_DISPLAY = (
    'QLabel {'
    '    background-color: #000000;'
    '    color: #ffffff;'
    '    padding: 10px 20px;'
    '}'
)

STYLE_BTN_GRAY = (
    'QPushButton {'
    '    background-color: #a5a5a5;'
    '    color: #000000;'
    '    border-radius: 40px;'
    '    font-size: 28px;'
    '    font-weight: bold;'
    '}'
    'QPushButton:pressed { background-color: #d4d4d4; }'
)

STYLE_BTN_DARK = (
    'QPushButton {'
    '    background-color: #333333;'
    '    color: #ffffff;'
    '    border-radius: 40px;'
    '    font-size: 28px;'
    '    font-weight: bold;'
    '}'
    'QPushButton:pressed { background-color: #737373; }'
)

STYLE_BTN_ORANGE = (
    'QPushButton {'
    '    background-color: #ff9f0a;'
    '    color: #ffffff;'
    '    border-radius: 40px;'
    '    font-size: 28px;'
    '    font-weight: bold;'
    '}'
    'QPushButton:pressed { background-color: #ffc966; }'
)

STYLE_BTN_ZERO = (
    'QPushButton {'
    '    background-color: #333333;'
    '    color: #ffffff;'
    '    border-radius: 40px;'
    '    font-size: 28px;'
    '    font-weight: bold;'
    '    text-align: left;'
    '    padding-left: 30px;'
    '}'
    'QPushButton:pressed { background-color: #737373; }'
)

BUTTON_LAYOUT = [
    ('AC',  0, 0, 1, 1, STYLE_BTN_GRAY),
    ('+/-', 0, 1, 1, 1, STYLE_BTN_GRAY),
    ('%',   0, 2, 1, 1, STYLE_BTN_GRAY),
    ('÷',   0, 3, 1, 1, STYLE_BTN_ORANGE),
    ('7',   1, 0, 1, 1, STYLE_BTN_DARK),
    ('8',   1, 1, 1, 1, STYLE_BTN_DARK),
    ('9',   1, 2, 1, 1, STYLE_BTN_DARK),
    ('×',   1, 3, 1, 1, STYLE_BTN_ORANGE),
    ('4',   2, 0, 1, 1, STYLE_BTN_DARK),
    ('5',   2, 1, 1, 1, STYLE_BTN_DARK),
    ('6',   2, 2, 1, 1, STYLE_BTN_DARK),
    ('−',   2, 3, 1, 1, STYLE_BTN_ORANGE),
    ('1',   3, 0, 1, 1, STYLE_BTN_DARK),
    ('2',   3, 1, 1, 1, STYLE_BTN_DARK),
    ('3',   3, 2, 1, 1, STYLE_BTN_DARK),
    ('+',   3, 3, 1, 1, STYLE_BTN_ORANGE),
    ('0',   4, 0, 1, 2, STYLE_BTN_ZERO),
    ('.',   4, 2, 1, 1, STYLE_BTN_DARK),
    ('=',   4, 3, 1, 1, STYLE_BTN_ORANGE),
]

OP_MAP = {'÷': '/', '×': '*', '−': '-', '+': '+'}


class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current = '0'
        self.stored = None
        self.op = None
        self.reset_next = False
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle('Calculator')
        self.setFixedSize(410, 620)
        self.setStyleSheet('background-color: #000000;')

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.display = QLabel('0')
        self.display.setStyleSheet(STYLE_DISPLAY)
        self.display.setFont(QFont('Helvetica Neue', 60, QFont.Light))
        self.display.setFixedHeight(150)
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        main_layout.addWidget(self.display)

        grid = QGridLayout()
        grid.setSpacing(10)
        main_layout.addLayout(grid)

        btn_size = 80

        for label, row, col, row_span, col_span, style in BUTTON_LAYOUT:
            btn = QPushButton(label)
            btn.setStyleSheet(style)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            if col_span == 2:
                btn.setMinimumSize(btn_size * 2 + 10, btn_size)
            else:
                btn.setMinimumSize(btn_size, btn_size)
            btn.clicked.connect(lambda checked, lbl=label: self._on_click(lbl))
            grid.addWidget(btn, row, col, row_span, col_span)

    def _update_display(self):
        text = self.current
        try:
            value = float(text)
            if value == int(value) and '.' not in text:
                text = f'{int(value):,}'
            else:
                integer_part, decimal_part = text.split('.')
                text = f'{int(integer_part):,}.{decimal_part}'
        except ValueError:
            pass
        self.display.setText(text)

    def _on_click(self, label):
        if label.isdigit():
            self._handle_digit(label)
        elif label == '.':
            self._handle_dot()
        elif label == 'AC':
            self._handle_ac()
        elif label == '+/-':
            self._handle_sign()
        elif label == '%':
            self._handle_percent()
        elif label == '=':
            self._handle_equals()
        elif label in OP_MAP:
            self._handle_operator(label)
        self._update_display()

    def _handle_digit(self, digit):
        if self.reset_next:
            self.current = digit
            self.reset_next = False
        elif self.current == '0':
            self.current = digit
        else:
            if len(self.current) < 9:
                self.current += digit

    def _handle_dot(self):
        if self.reset_next:
            self.current = '0.'
            self.reset_next = False
        elif '.' not in self.current:
            self.current += '.'

    def _handle_ac(self):
        self.current = '0'
        self.stored = None
        self.op = None
        self.reset_next = False

    def _handle_sign(self):
        if self.current != '0':
            if self.current.startswith('-'):
                self.current = self.current[1:]
            else:
                self.current = '-' + self.current

    def _handle_percent(self):
        try:
            value = float(self.current) / 100
            self.current = str(value)
        except ValueError:
            pass

    def _handle_operator(self, op):
        self._handle_equals()
        self.stored = float(self.current)
        self.op = OP_MAP[op]
        self.reset_next = True

    def _handle_equals(self):
        if self.op is None or self.stored is None:
            return
        try:
            result = eval(f'{self.stored}{self.op}{float(self.current)}')
            if result == int(result):
                self.current = str(int(result))
            else:
                self.current = f'{result:.8g}'
        except ZeroDivisionError:
            self.current = 'Error'
        self.stored = None
        self.op = None
        self.reset_next = True


def main():
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
