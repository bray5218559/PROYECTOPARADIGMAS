# modelos/game_logic.py
import random
from typing import List, Tuple

class MinesweeperGame:
    def __init__(self, rows: int, cols: int, mines: int):
        self.rows = rows
        self.cols = cols
        self.mines = mines

        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flagged = [[False for _ in range(cols)] for _ in range(rows)]

        self.game_over = False
        self.game_won = False
        self.first_click = True

        self.mine_positions: List[Tuple[int, int]] = []

    def place_mines_after_first_click(self, first_row: int, first_col: int):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        if (first_row, first_col) in positions:
            positions.remove((first_row, first_col))

        self.mine_positions = random.sample(positions, self.mines)
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        for r, c in self.mine_positions:
            self.board[r][c] = -1

        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1:
                    self.board[r][c] = self.count_adjacent_mines(r, c)

    def count_adjacent_mines(self, row: int, col: int) -> int:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.board[nr][nc] == -1:
                        count += 1
        return count

    def reveal(self, row: int, col: int) -> bool:
        if self.first_click:
            self.place_mines_after_first_click(row, col)
            self.first_click = False

        if (row, col) in self.mine_positions:
            return False

        if not self.revealed[row][col] and not self.flagged[row][col]:
            self.revealed[row][col] = True

            if self.board[row][col] == 0:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                                self.reveal(nr, nc)

        self.check_win()
        return True

    def toggle_flag(self, row: int, col: int) -> None:
        if not self.revealed[row][col]:
            self.flagged[row][col] = not self.flagged[row][col]
            self.check_win()

    def check_win(self) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1 and not self.revealed[r][c]:
                    return
        self.game_won = True