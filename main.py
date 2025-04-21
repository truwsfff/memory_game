import sys
import random
from PyQt6.QtWidgets import (QWidget, QPushButton, QLabel, QApplication,
                             QMessageBox, QGridLayout)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPalette, QColor


class MinesweeperLogic(QWidget):
    def __init__(self, difficult, name):
        super().__init__()
        self.difficult = difficult
        self.login = name
        self.counter = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_lab)
        self.timer.start(1000)
        self.timer_label = QLabel('Время: 0', self)
        self.timer_label.resize(120, 25)
        self.timer_label.setStyleSheet('color: white; font-size: 18px;')

        self.exit_button = QPushButton('Выход', self)
        self.exit_button.clicked.connect(self.exit_menu_before)
        self.exit_button.setStyleSheet("font-size: 18px;")

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#121212'))
        self.setPalette(palette)

        if self.difficult == 0:
            grid_size = (8, 8)
            field_size = (320, 320)
            self.setFixedSize(650, 500)
        elif self.difficult == 1:
            grid_size = (15, 15)
            field_size = (600, 600)
            self.setFixedSize(850, 700)
        else:
            grid_size = (20, 20)
            field_size = (800, 800)
            self.setFixedSize(1100, 900)

        self.buttons_container = QWidget(self)
        self.buttons_container.setGeometry(30, 50, field_size[0],
                                           field_size[1])
        self.createGrid(grid_size)

        self.setup_digit_panel()

        self.timer_label.move(30, 10)
        self.exit_button.move(30, self.height() - 50)

        self.active_challenge = False
        self.current_challenge = {}
        self.current_base = None
        self.selected_digit = None
        self.challenge_timer = QTimer(self)
        self.challenge_timer.setSingleShot(True)
        self.challenge_timer.timeout.connect(self.hideChallengeNumbers)

    def setup_digit_panel(self):
        self.digit_panel = QWidget(self)
        digit_layout = QGridLayout()
        digit_layout.setSpacing(10)

        self.digit_buttons = {}
        for d in range(10):
            btn = QPushButton(str(d), self.digit_panel)
            btn.setFixedSize(70, 60)
            btn.setStyleSheet("font-size: 20px;")
            btn.clicked.connect(
                lambda checked, digit=d: self.selectDigit(digit))
            row = d // 2
            col = d % 2
            digit_layout.addWidget(btn, row, col)
            self.digit_buttons[d] = btn

        self.digit_panel.setLayout(digit_layout)
        self.digit_panel.setGeometry(self.width() - 180, 80, 160,
                                     self.height() - 150)

    def createGrid(self, grid_size):
        rows, cols = grid_size
        self.matrix = []
        self.buttons = {}
        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        for i in range(rows):
            row = []
            for j in range(cols):
                btn = QPushButton(self)
                btn.setFixedSize(40, 40)
                btn.setStyleSheet(
                    "border: 1px solid gray; background-color: lightgray; "
                    "font-size: 18px; color: black;")
                btn.clicked.connect(
                    lambda checked, x=i, y=j: self.cellClicked(x, y))
                grid.addWidget(btn, i, j)
                self.buttons[(i, j)] = btn
                row.append(
                    {"revealed": False, "challenge": None, "solved": False})
            self.matrix.append(row)
        self.buttons_container.setLayout(grid)

    def cellClicked(self, x, y):
        if (self.challenge_timer.isActive() or self.matrix[x][y]["revealed"]
                or \
                self.matrix[x][y]['solved']):
            return

        if not self.active_challenge:
            self.matrix[x][y]["revealed"] = True
            self.buttons[(x, y)].setText("")
            self.buttons[(x, y)].setStyleSheet(
                "background-color: white; color: black;")
            neighbors = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in
                         (-1, 0, 1) if not (dx == 0 and dy == 0)]
            valid_neighbors = []
            for (nx, ny) in neighbors:
                if 0 <= nx < len(self.matrix) and 0 <= ny < len(
                        self.matrix[0]) and not self.matrix[nx][ny][
                    "revealed"] and not self.matrix[nx][ny]['solved']:
                    valid_neighbors.append((nx, ny))
            if not valid_neighbors:
                if self.checkVictory():
                    self.victoryMessage()
                return
            self.current_challenge = {}
            for (nx, ny) in valid_neighbors:
                rand_digit = random.randint(0, 9)
                self.matrix[nx][ny]["challenge"] = rand_digit
                self.buttons[(nx, ny)].setText(str(rand_digit))
                self.current_challenge[(nx, ny)] = rand_digit
            self.current_base = (x, y)
            self.active_challenge = True
            self.challenge_timer.start(10000)
        else:
            if (x, y) in self.current_challenge and not self.matrix[x][y][
                "solved"]:
                if self.selected_digit is None:
                    return
                correct_digit = self.current_challenge[(x, y)]
                if self.selected_digit == correct_digit:
                    self.matrix[x][y]["solved"] = True
                    self.buttons[(x, y)].setText(str(correct_digit))
                    self.buttons[(x, y)].setStyleSheet(
                        "background-color: lightgreen; font-size: 18px; "
                        "color: black;")
                    del self.current_challenge[(x, y)]
                    self.selected_digit = None
                    for btn in self.digit_buttons.values():
                        btn.setStyleSheet("font-size: 20px;")
                    print(self.matrix)
                    if not self.current_challenge:
                        self.active_challenge = False
                        self.current_base = None
                        if self.checkVictory():
                            self.victoryMessage()
                else:
                    self.buttons[(x, y)].setStyleSheet(
                        "background-color: red;")
                    self.gameOver()

    def hideChallengeNumbers(self):
        for (x, y), value in self.current_challenge.items():
            if not self.matrix[x][y]["solved"]:
                self.buttons[(x, y)].setText("")
        self.selected_digit = None
        for btn in self.digit_buttons.values():
            btn.setStyleSheet("font-size: 20px;")

    def selectDigit(self, digit):
        if not self.active_challenge:
            return
        self.selected_digit = digit
        for d, btn in self.digit_buttons.items():
            if d == digit:
                btn.setStyleSheet("background-color: yellow; font-size: 20px;")
            else:
                btn.setStyleSheet("font-size: 20px;")

    def timer_lab(self):
        self.counter += 1
        self.timer_label.setText(f'Время: {self.counter}')

    def gameOver(self):
        self.challenge_timer.stop()
        self.timer.stop()
        for btn in self.buttons.values():
            btn.setEnabled(False)
        msg = QMessageBox(self)
        msg.setWindowTitle("Game Over")
        msg.setText("Неверная цифра! Игра окончена.")
        msg.exec()

    def checkVictory(self):
        for row in self.matrix:
            for cell in row:
                if cell["challenge"] is None and not cell["solved"] and not \
                cell['revealed']:
                    print(1)
                    return False
        return True

    def victoryMessage(self):
        self.timer.stop()
        msg = QMessageBox(self)
        msg.setWindowTitle("Победа!")
        msg.setText(
            f"Поздравляем, {self.login}! Вы отгадали все цифры за "
            f"{self.counter} секунд.")
        msg.exec()

    def exit_menu_before(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MinesweeperLogic(0, "Игрок")
    window.show()
    sys.exit(app.exec())
