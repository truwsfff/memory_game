import sys
import random
from PyQt6.QtWidgets import (QWidget, QPushButton, QLabel, QGridLayout,
                             QVBoxLayout, QApplication, QMessageBox)
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
        self.timer_label.setStyleSheet('color: white;')

        self.exit_button = QPushButton('Выход', self)
        self.exit_button.clicked.connect(self.exit_menu_before)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#121212'))
        self.setPalette(palette)

        if self.difficult == 0:
            grid_size = (10, 10)
            field_size = (250, 250)
            self.setFixedSize(400, 400)
        elif self.difficult == 1:
            grid_size = (15, 15)
            field_size = (375, 375)
            self.setFixedSize(550, 550)
        else:
            grid_size = (20, 20)
            field_size = (500, 500)
            self.setFixedSize(800, 800)

        self.buttons_container = QWidget(self)
        self.buttons_container.setGeometry(50, 50, field_size[0], field_size[1])
        self.createGrid(grid_size)

        self.digit_panel = QWidget(self)
        digit_layout = QVBoxLayout()
        self.digit_buttons = {}
        for d in range(10):
            btn = QPushButton(str(d), self.digit_panel)
            btn.setStyleSheet("color: black;")
            btn.clicked.connect(lambda checked, digit=d: self.selectDigit(digit))
            digit_layout.addWidget(btn)
            self.digit_buttons[d] = btn
            btn.setEnabled(False)
        self.digit_panel.setLayout(digit_layout)
        self.digit_panel.setGeometry(self.width() - 80, 50,
                                     70, self.height() - 100)

        self.timer_label.move(50, 10)
        self.exit_button.move(10, self.height() - 50)

        self.active_challenge = False
        self.current_challenge = {}
        self.current_base = None
        self.selected_digit = None
        self.challenge_timer = QTimer(self)
        self.challenge_timer.setSingleShot(True)
        self.challenge_timer.timeout.connect(self.hideChallengeNumbers)

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
                btn.setFixedSize(25, 25)
                btn.setStyleSheet(
                    "border: 1px solid gray; background-color: lightgray; color: black;")
                btn.clicked.connect(
                    lambda checked, x=i, y=j: self.cellClicked(x, y))
                grid.addWidget(btn, i, j)
                self.buttons[(i, j)] = btn
                row.append(
                    {"revealed": False, "challenge": None, "solved": False})
            self.matrix.append(row)
        self.buttons_container.setLayout(grid)

    def cellClicked(self, x, y):
        if not self.active_challenge:
            if self.matrix[x][y]["revealed"] or self.matrix[x][y]["solved"]:
                return

            self.matrix[x][y]["revealed"] = True
            self.buttons[(x, y)].setText("")
            self.buttons[(x, y)].setStyleSheet(
                "background-color: white; color: black;")

            neighbors = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                         (x, y - 1),             (x, y + 1),
                         (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
            valid_neighbors = [
                (nx, ny)
                for nx, ny in neighbors
                if 0 <= nx < len(self.matrix)
                and 0 <= ny < len(self.matrix[0])
            ]

            for nx, ny in valid_neighbors:
                rand_digit = random.randint(0, 9)
                self.matrix[nx][ny]["challenge"] = rand_digit
                btn = self.buttons[(nx, ny)]
                btn.setText(str(rand_digit))

            self.current_challenge = {
                (nx, ny): self.matrix[nx][ny]["challenge"]
                for nx, ny in valid_neighbors
            }
            self.current_base = (x, y)
            self.active_challenge = True

            for btn in self.digit_buttons.values():
                btn.setEnabled(False)

            self.challenge_timer.start(10000)
        else:
            if (x, y) in self.current_challenge and not self.matrix[x][y][
                "solved"
            ]:
                if self.selected_digit is None:
                    return
                correct = self.current_challenge[(x, y)]
                btn = self.buttons[(x, y)]
                if self.selected_digit == correct:
                    self.matrix[x][y]["solved"] = True
                    btn.setText(str(correct))
                    btn.setStyleSheet("background-color: lightgreen; color: black;")
                    del self.current_challenge[(x, y)]
                    self.selected_digit = None
                    for b in self.digit_buttons.values():
                        b.setStyleSheet("color: black;")

                    if not self.current_challenge:
                        self.active_challenge = False
                        self.current_base = None
                        for b in self.digit_buttons.values():
                            b.setEnabled(False)
                else:
                    btn.setStyleSheet("background-color: red; color: white;")
                    self.gameOver()

    def hideChallengeNumbers(self):
        for (x, y) in list(self.current_challenge.keys()):
            self.buttons[(x, y)].setText("")
        for btn in self.digit_buttons.values():
            btn.setEnabled(True)

    def selectDigit(self, digit):
        if not self.active_challenge:
            return
        self.selected_digit = digit
        for d, btn in self.digit_buttons.items():
            if d == digit:
                btn.setStyleSheet("background-color: yellow; color: black;")
            else:
                btn.setStyleSheet("color: black;")

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

    def exit_menu_before(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MinesweeperLogic(0, "Player")
    window.show()
    sys.exit(app.exec())
