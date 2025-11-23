# main.py
import flet as ft
import time
import sys
import os
from modelos.database import DatabaseManager, UserDAO, GameDAO
from controladores.user_controller import UserController
from controladores.game_controller import GameController
from vistas.ui_components import UIComponents

def main(page: ft.Page):
    # Configuración de la página
    page.title = "Buscaminas"
    page.theme_mode = "light"
    page.padding = 20
    page.horizontal_alignment = "center"

    # Inicialización de componentes
    db_manager = DatabaseManager()
    user_dao = UserDAO(db_manager)
    game_dao = GameDAO(db_manager)
    
    user_controller = UserController(user_dao)
    game_controller = GameController(game_dao)

    # Componentes de UI básicos
    ui = UIComponents()
    title = ui.create_title()
    difficulty_text = ui.create_difficulty_text()
    mines_counter = ui.create_mines_counter()
    status_message = ui.create_status_message()

    # Variables para controlar diálogos actuales
    current_user_dialog = None
    current_stats_dialog = None

    # Funciones auxiliares para diálogos
    def close_current_dialog():
        if current_user_dialog:
            current_user_dialog.open = False
        if current_stats_dialog:
            current_stats_dialog.open = False
        page.update()

    # Funciones de eventos PRINCIPALES
    def on_cell_click(row: int, col: int):
        success, game_ended = game_controller.reveal_cell(row, col)
        
        if not success:  # Perdió
            status_message.value = "\U0001F4A5 ¡Perdiste! Haz click en 'Continuar' para jugar de nuevo"
            status_message.color = "red"
            reveal_all_mines()
            if user_controller.current_user:
                duration = int(time.time() - game_controller.game_start_time)
                user_controller.update_user_stats(False, duration, game_controller.get_difficulty())
        elif game_ended and game_controller.current_game.game_won:  # Ganó
            status_message.value = "\U0001F389 ¡Ganaste! ¡Felicidades!"
            status_message.color = "green"
            if user_controller.current_user:
                duration = int(time.time() - game_controller.game_start_time)
                user_controller.update_user_stats(True, duration, game_controller.get_difficulty())
        else:  # Juego en progreso
            status_message.value = "¡Sigue así!"
            status_message.color = "green"
        
        update_display()
        update_mines_counter()

    def on_cell_long_press(row: int, col: int):
        game_controller.toggle_flag(row, col)
        update_display()
        update_mines_counter()

    def on_easy_click(_):
        start_new_game(8, 8, 10, "Fácil")

    def on_medium_click(_):
        start_new_game(12, 12, 30, "Medio")

    def on_hard_click(_):
        start_new_game(16, 16, 60, "Difícil")

    def on_continue_click(_):
        if game_controller.current_game:
            start_new_game(
                game_controller.current_game.rows,
                game_controller.current_game.cols,
                game_controller.current_game.mines,
                game_controller.get_difficulty()
            )

    def on_exit_click(_):
        print("Cerrando juego...")
        # Método correcto para cerrar la aplicación en Flet
        import sys
        sys.exit()

    # Funciones específicas para diálogos de usuario
    def on_user_click(_):
        show_user_dialog()

    def on_stats_click(_):
        show_stats_dialog()

    def on_login_click(_):
        nonlocal current_user_dialog
        if current_user_dialog:
            username = current_user_dialog.content.controls[0].value.strip()
            success, message = user_controller.login(username)
            
            current_user_dialog.content.controls[2].value = message
            if success:
                current_user_dialog.open = False
                status_message.value = message
                status_message.color = "green"
            page.update()

    def on_register_click(_):
        nonlocal current_user_dialog
        if current_user_dialog:
            username = current_user_dialog.content.controls[0].value.strip()
            email = current_user_dialog.content.controls[1].value.strip() or None
            success, message = user_controller.register(username, email)
            
            current_user_dialog.content.controls[2].value = message
            if success:
                current_user_dialog.open = False
                status_message.value = message
                status_message.color = "green"
            page.update()

    def on_close_user_dialog(_):
        nonlocal current_user_dialog
        if current_user_dialog:
            current_user_dialog.open = False
            page.update()

    def on_close_stats_dialog(_):
        nonlocal current_stats_dialog
        if current_stats_dialog:
            current_stats_dialog.open = False
            page.update()

    # Funciones auxiliares del juego
    def start_new_game(rows: int, cols: int, mines: int, difficulty: str):
        user_id = user_controller.current_user.id if user_controller.current_user else None
        game_controller.start_new_game(rows, cols, mines, difficulty, user_id)
        
        difficulty_text.value = f"Dificultad: {difficulty}"
        status_message.value = "¡Nuevo juego comenzado!"
        status_message.color = "blue"
        
        update_display()
        update_mines_counter()

    def update_display():
        if not game_grid:
            return
            
        game_grid.controls.clear()
        game_state = game_controller.get_game_state()
        
        if not game_state:
            page.update()
            return

        game_grid.runs_count = game_state['cols']
        
        for r in range(game_state['rows']):
            for c in range(game_state['cols']):
                if game_state['revealed'][r][c]:
                    value = game_state['board'][r][c]
                    bgcolor = "white"
                    text_color = "black"

                    if value == -1:
                        content = "\U0001F4A3"
                        bgcolor = "red200"
                    elif value > 0:
                        content = str(value)
                        colors = ["blue", "green", "red", "purple", "maroon", "teal", "black", "grey"]
                        text_color = colors[value - 1] if 0 < value <= 8 else "black"
                    else:
                        content = ""

                    cell = ft.Container(
                        content=ft.Text(content, size=12, color=text_color),
                        width=35, height=35,
                        alignment=ft.alignment.center,
                        bgcolor=bgcolor,
                        border=ft.border.all(1, "grey400"),
                        border_radius=2,
                    )
                else:
                    if game_state['flagged'][r][c]:
                        content = "\U0001F6A9"
                        bgcolor = "orange200"
                    else:
                        content = ""
                        bgcolor = "grey400"

                    cell = ui.create_cell_button(r, c, on_cell_click, on_cell_long_press)
                    cell.content = ft.Text(content, size=12)
                    cell.bgcolor = bgcolor

                game_grid.controls.append(cell)
        
        page.update()

    def update_mines_counter():
        mines_counter.value = f"Minas: {game_controller.get_remaining_mines()}"
        page.update()

    def reveal_all_mines():
        game_state = game_controller.get_game_state()
        if game_state:
            for r in range(game_state['rows']):
                for c in range(game_state['cols']):
                    if game_state['board'][r][c] == -1:
                        game_state['revealed'][r][c] = True
            update_display()

    def show_user_dialog():
        nonlocal current_user_dialog
        close_current_dialog()  # Cerrar cualquier diálogo abierto
        current_user_dialog = ui.create_user_dialog(on_login_click, on_register_click, on_close_user_dialog)
        page.dialog = current_user_dialog
        current_user_dialog.open = True
        page.update()

    def show_stats_dialog():
        nonlocal current_stats_dialog
        if user_controller.current_user:
            close_current_dialog()  # Cerrar cualquier diálogo abierto
            stats_data = user_controller.get_user_stats()
            current_stats_dialog = ui.create_stats_dialog(stats_data, on_close_stats_dialog)
            page.dialog = current_stats_dialog
            current_stats_dialog.open = True
            page.update()
        else:
            status_message.value = "Primero debes iniciar sesión"
            status_message.color = "red"
            page.update()

    # CREAR COMPONENTES UI DESPUÉS de definir todas las funciones
    game_grid = ui.create_game_grid(8, 8, on_cell_click, on_cell_long_press)
    
    difficulty_buttons = ui.create_difficulty_buttons(
        on_easy_click, on_medium_click, on_hard_click
    )
    
    action_buttons = ui.create_action_buttons(
        on_continue_click, on_exit_click, on_user_click, on_stats_click
    )
    
    instructions = ui.create_instructions()

    # Ensamblar interfaz
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

    # Iniciar juego por defecto
    start_new_game(8, 8, 10, "Fácil")
    # Mostrar diálogo de usuario al inicio
    show_user_dialog()

if __name__ == "__main__":
    ft.app(target=main)