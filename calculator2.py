import math
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

MAX_DIGITS = 9


class Calculator:
    """계산기 핵심 로직 클래스."""

    def __init__(self):
        self._current = '0'
        self._stored = None
        self._op = None
        self._reset_next = False
        self._error = False

    def input_digit(self, digit):
        if self._error:
            return
        if self._reset_next:
            self._current = digit
            self._reset_next = False
            return
        if self._current == '0':
            self._current = digit
        else:
            digits_only = self._current.replace('-', '').replace('.', '')
            if len(digits_only) < MAX_DIGITS:
                self._current += digit

    def input_dot(self):
        if self._error:
            return
        if self._reset_next:
            self._current = '0.'
            self._reset_next = False
            return
        if '.' not in self._current:
            self._current += '.'

    def reset(self):
        self._current = '0'
        self._stored = None
        self._op = None
        self._reset_next = False
        self._error = False

    def negative_positive(self):
        if self._error or self._current == '0':
            return
        if self._current.startswith('-'):
            self._current = self._current[1:]
        else:
            self._current = '-' + self._current

    def percent(self):
        if self._error:
            return
        try:
            value = float(self._current) / 100
            self._current = self._format_result(value)
        except (ValueError, OverflowError):
            self._set_error('Error')

    def add(self):
        self._apply_operator('+')

    def subtract(self):
        self._apply_operator('-')

    def multiply(self):
        self._apply_operator('*')

    def divide(self):
        self._apply_operator('/')

    def equal(self):
        if self._op is None or self._stored is None:
            return
        try:
            current_val = float(self._current)
            if self._op == '+':
                result = self._stored + current_val
            elif self._op == '-':
                result = self._stored - current_val
            elif self._op == '*':
                result = self._stored * current_val
            elif self._op == '/':
                if current_val == 0:
                    raise ZeroDivisionError
                result = self._stored / current_val
            else:
                return
            if math.isinf(result) or math.isnan(result):
                raise OverflowError
            self._current = self._format_result(result)
        except ZeroDivisionError:
            self._set_error('나눌 수 없음')
            return
        except OverflowError:
            self._set_error('범위 초과')
            return
        except ValueError:
            self._set_error('Error')
            return
        self._stored = None
        self._op = None
        self._reset_next = True

    def get_display(self):
        return self._current

    def _apply_operator(self, op):
        if self._error:
            return
        if self._op is not None and not self._reset_next:
            self.equal()
        if not self._error:
            try:
                self._stored = float(self._current)
                self._op = op
                self._reset_next = True
            except ValueError:
                self._set_error('Error')

    def _set_error(self, message):
        self._current = message
        self._error = True
        self._stored = None
        self._op = None

    @staticmethod
    def _format_result(value):
        if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        rounded = round(value, 6)
        if isinstance(rounded, float) and rounded.is_integer():
            return str(int(rounded))
        return f'{rounded:.6f}'.rstrip('0').rstrip('.')


class CalculatorWindow(QMainWindow):
    """계산기 UI 클래스."""

    def __init__(self):
        super().__init__()
        self._calc = Calculator()
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

    def _on_click(self, label):
        calc = self._calc
        if label.isdigit():
            calc.input_digit(label)
        elif label == '.':
            calc.input_dot()
        elif label == 'AC':
            calc.reset()
        elif label == '+/-':
            calc.negative_positive()
        elif label == '%':
            calc.percent()
        elif label == '=':
            calc.equal()
        elif label == '÷':
            calc.divide()
        elif label == '×':
            calc.multiply()
        elif label == '−':
            calc.subtract()
        elif label == '+':
            calc.add()
        self._update_display()

    def _update_display(self):
        raw = self._calc.get_display()
        text = self._format_display(raw)
        self.display.setText(text)
        length = len(text)
        if length <= 6:
            font_size = 60
        elif length <= 9:
            font_size = 48
        elif length <= 12:
            font_size = 36
        else:
            font_size = 24
        self.display.setFont(QFont('Helvetica Neue', font_size, QFont.Light))

    @staticmethod
    def _format_display(text):
        if text in ('나눌 수 없음', '범위 초과', 'Error'):
            return text
        try:
            if '.' in text:
                sign = '-' if text.startswith('-') else ''
                abs_text = text.lstrip('-')
                integer_part, decimal_part = abs_text.split('.')
                return f'{sign}{int(integer_part):,}.{decimal_part}'
            return f'{int(text):,}'
        except ValueError:
            return text


def main():
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
