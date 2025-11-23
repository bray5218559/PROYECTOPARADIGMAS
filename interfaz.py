import flet as ft
import random


class MinesweeperGame:
    def __init__(self, rows: int, cols: int, mines: int):
        self.rows = rows
        self.cols = cols
        self.mines = mines

        # -1 = mina, 0..8 = número de minas alrededor
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flagged = [[False for _ in range(cols)] for _ in range(rows)]

        self.game_over = False
        self.game_won = False
        self.first_click = True

        # Sin colocar minas aún: primera jugada segura
        self.mine_positions: list[tuple[int, int]] = []

    # Mantener por compatibilidad (no coloca minas hasta el primer click)
    def place_mines(self):
        self.mine_positions = []

    def place_mines_after_first_click(self, first_row: int, first_col: int):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        # Evitar que la primera celda sea mina
        if (first_row, first_col) in positions:
            positions.remove((first_row, first_col))

        self.mine_positions = random.sample(positions, self.mines)

        # Reiniciar tablero de números
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # Colocar minas
        for r, c in self.mine_positions:
            self.board[r][c] = -1

        # Calcular conteos
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

        # Click en mina
        if (row, col) in self.mine_positions:
            return False

        if not self.revealed[row][col] and not self.flagged[row][col]:
            self.revealed[row][col] = True

            # Si es un 0, expandir región (flood fill DFS)
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


def main(page: ft.Page):
    page.title = "Buscaminas"
    page.theme_mode = "light"
    page.padding = 20
    page.horizontal_alignment = "center"

    current_game: MinesweeperGame | None = None
    difficulty_level = "Fácil"

    title = ft.Text("BUSCAMINAS", size=32, weight="bold", color="blue900")
    difficulty_text = ft.Text("Dificultad: Fácil", size=16)
    mines_counter = ft.Text("Minas: 0", size=16, weight="bold")
    status_message = ft.Text("", size=18, weight="bold")

    game_grid = ft.GridView(
        expand=1,
        runs_count=8,  # se actualiza dinámicamente al pintar
        max_extent=35,
        spacing=2,
        run_spacing=2,
    )

    def create_cell_button(row: int, col: int) -> ft.Container:
        def on_click(_):
            nonlocal status_message
            if current_game and not current_game.game_over and not current_game.game_won:
                if not current_game.reveal(row, col):
                    current_game.game_over = True
                    status_message.value = "\U0001F4A5 ¡Perdiste! Haz click en 'Continuar' para jugar de nuevo"
                    status_message.color = "red"
                    reveal_all_mines()
                else:
                    status_message.value = "¡Sigue así!"
                    status_message.color = "green"
                update_display()
                if current_game.game_won:
                    status_message.value = "\U0001F389 ¡Ganaste! ¡Felicidades!"
                    status_message.color = "green"
                    page.update()

        def on_long_press(_):
            if current_game and not current_game.game_over and not current_game.game_won:
                current_game.toggle_flag(row, col)
                update_mines_counter()
                update_display()

        return ft.Container(
            content=ft.Text("", size=12),
            width=35,
            height=35,
            alignment=ft.alignment.center,
            bgcolor="grey300",
            border_radius=3,
            on_click=on_click,
            on_long_press=on_long_press,
        )

    def update_display():
        game_grid.controls.clear()
        if not current_game:
            page.update()
            return

        # ajustar columnas visibles al tablero actual
        game_grid.runs_count = current_game.cols

        for r in range(current_game.rows):
            for c in range(current_game.cols):
                if current_game.revealed[r][c]:
                    value = current_game.board[r][c]
                    bgcolor = "white"
                    text_color = "black"

                    if value == -1:
                        content = "\U0001F4A3"
                        bgcolor = "red200"
                    elif value > 0:
                        content = str(value)
                        # Colores para números 1..8
                        colors = [
                            "blue", "green", "red", "purple",
                            "maroon", "teal", "black", "grey",
                        ]
                        text_color = colors[value - 1] if 0 < value <= 8 else "black"
                    else:
                        content = ""

                    cell = ft.Container(
                        content=ft.Text(content, size=12, color=text_color),
                        width=35,
                        height=35,
                        alignment=ft.alignment.center,
                        bgcolor=bgcolor,
                        border=ft.border.all(1, "grey400"),
                        border_radius=2,
                    )
                else:
                    # Celda oculta
                    if current_game.flagged[r][c]:
                        content = "\U0001F6A9"  # 🚩
                        bgcolor = "orange200"
                    else:
                        content = ""
                        bgcolor = "grey400"

                    cell = create_cell_button(r, c)
                    cell.content = ft.Text(content, size=12)
                    cell.bgcolor = bgcolor

                game_grid.controls.append(cell)

        page.update()

    def update_mines_counter():
        if current_game:
            flagged_count = sum(sum(1 for v in row if v) for row in current_game.flagged)
            mines_counter.value = f"Minas: {current_game.mines - flagged_count}"
        else:
            mines_counter.value = "Minas: 0"
        page.update()

    def reveal_all_mines():
        if current_game:
            for r, c in current_game.mine_positions:
                current_game.revealed[r][c] = True
            update_display()

    def start_new_game(rows: int, cols: int, mines: int, difficulty: str):
        nonlocal current_game, difficulty_level
        current_game = MinesweeperGame(rows, cols, mines)
        difficulty_level = difficulty
        difficulty_text.value = f"Dificultad: {difficulty}"
        status_message.value = "¡Nuevo juego comenzado!"
        status_message.color = "blue"
        update_mines_counter()
        update_display()

    def on_easy_click(_):
        start_new_game(8, 8, 10, "Fácil")

    def on_medium_click(_):
        start_new_game(12, 12, 30, "Medio")

    def on_hard_click(_):
        start_new_game(16, 16, 60, "Difícil")

    def on_continue_click(_):
        if current_game:
            start_new_game(current_game.rows, current_game.cols, current_game.mines, difficulty_level)

    def on_exit_click(_):
        page.window_destroy()

    difficulty_buttons = ft.Row(
        controls=[
            ft.ElevatedButton(
                "Fácil (8x8 - 10 minas)", on_click=on_easy_click, bgcolor="green400", color="white"
            ),
            ft.ElevatedButton(
                "Medio (12x12 - 30 minas)", on_click=on_medium_click, bgcolor="orange400", color="white"
            ),
            ft.ElevatedButton(
                "Difícil (16x16 - 60 minas)", on_click=on_hard_click, bgcolor="red400", color="white"
            ),
        ],
        alignment="center",
        spacing=10,
    )

    action_buttons = ft.Row(
        controls=[
            ft.ElevatedButton(
                "Continuar", icon="replay", on_click=on_continue_click, bgcolor="blue400", color="white"
            ),
            ft.ElevatedButton(
                "Salir del Juego", icon="exit_to_app", on_click=on_exit_click, bgcolor="red400", color="white"
            ),
        ],
        alignment="center",
        spacing=20,
    )

    instructions = ft.Container(
        content=ft.Column(
            [
                ft.Text("Instrucciones:", weight="bold"),
                ft.Text("• Click izquierdo: Revelar celda"),
                ft.Text("• Click largo o derecho: Colocar/remover bandera"),
                ft.Text("• Objetivo: Revelar todas las celdas sin minas"),
            ],
            spacing=5,
        ),
        padding=10,
        bgcolor="grey100",
        border_radius=10,
        margin=10,
    )

    page.add(
        title,
        difficulty_buttons,
        ft.Row([difficulty_text, mines_counter], alignment="spaceBetween"),
        status_message,
        ft.Container(
            content=game_grid,
            width=400,
            height=400,
            padding=10,
            bgcolor="grey200",
            border_radius=10,
        ),
        action_buttons,
        instructions,
    )

    # Juego por defecto
    start_new_game(8, 8, 10, "Fácil")


if __name__ == "__main__":
    ft.app(target=main)
