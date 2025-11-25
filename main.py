# main.py
import flet as ft
import time
from modelos.json_database import JSONDatabase, UserDAO, GameDAO
from controladores.user_controller import UserController
from controladores.game_controller import GameController
from vistas.ui_components import UIComponents, StatsDialog

class MinesweeperApp:
    def __init__(self):
        # Inicializar base de datos JSON
        self.json_db = JSONDatabase()
        self.user_dao = UserDAO(self.json_db)
        self.game_dao = GameDAO(self.json_db)
        
        # Inicializar controladores
        self.user_controller = UserController(self.user_dao)
        self.game_controller = GameController(self.game_dao)
        
        # Componentes de UI
        self.ui = UIComponents()
        
        # Diálogos
        self.stats_dialog = None
        
        # Elementos de UI
        self.title = self.ui.create_title()
        self.difficulty_text = self.ui.create_difficulty_text()
        self.mines_counter = self.ui.create_mines_counter()
        self.status_message = self.ui.create_status_message()
        self.game_grid = None
        self.instructions = self.ui.create_instructions()
        
        # Estados
        self.current_page = "login"

    def build(self, page: ft.Page):
        self.page = page
        page.title = "Buscaminas"
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"
        page.theme_mode = "light"
        page.padding = 20
        
        # Mostrar página de login inicialmente
        self.show_login_page()

    def show_login_page(self, e=None):
        """Muestra la página de login/registro"""
        self.current_page = "login"
        
        # Crear formulario de login/registro directamente en la página
        self.username_field = ft.TextField(
            label="Nombre de usuario", 
            width=300,
            autofocus=True,
            hint_text="Ejemplo: maria"
        )
        self.email_field = ft.TextField(
            label="Email (opcional)", 
            width=300,
            hint_text="Ejemplo: maria@email.com"
        )
        self.message_text = ft.Text("", color="red", size=12)
        
        login_form = ft.Column([
            self.title,
            ft.Text("Bienvenido al Buscaminas", size=20, weight="bold"),
            ft.Text("Por favor, inicia sesión o regístrate para continuar", size=16),
            ft.Divider(),
            
            ft.Text("Nombre de usuario:", weight="bold"),
            self.username_field,
            
            ft.Text("Email (opcional):", weight="bold"),
            self.email_field,
            
            self.message_text,
            
            ft.Row([
                ft.ElevatedButton(
                    "Iniciar Sesión",
                    icon=ft.icons.LOGIN,
                    on_click=self.handle_login,
                    bgcolor="blue400",
                    color="white",
                    width=150
                ),
                ft.ElevatedButton(
                    "Registrarse",
                    icon=ft.icons.PERSON_ADD,
                    on_click=self.handle_register,
                    bgcolor="green400",
                    color="white",
                    width=150
                )
            ], alignment="center", spacing=20),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("¿Primera vez?", weight="bold"),
                    ft.Text("1. Ingresa tu nombre de usuario"),
                    ft.Text("2. Haz click en 'Registrarse'"),
                    ft.Text("3. Luego podrás iniciar sesión"),
                ], spacing=5),
                padding=10,
                bgcolor="blue50",
                border_radius=10,
                margin=10
            )
        ], alignment="center", horizontal_alignment="center", spacing=15)
        
        self.page.clean()
        self.page.add(login_form)

    def show_difficulty_selection(self, e=None):
        """Muestra la selección de dificultad"""
        self.current_page = "difficulty"
        
        difficulty_buttons = self.ui.create_difficulty_buttons(
            on_easy=lambda e: self.start_game("Fácil", 8, 8, 10),
            on_medium=lambda e: self.start_game("Medio", 12, 12, 30),
            on_hard=lambda e: self.start_game("Difícil", 16, 16, 60)
        )
        
        action_buttons = self.ui.create_action_buttons(
            on_user=lambda e: self.show_login_page(),
            on_stats=lambda e: self.show_stats_dialog(e),
            on_new_game=lambda e: self.show_difficulty_selection(),
            on_exit=lambda e: self.exit_app(e)
        )
        
        user_info = ft.Row([
            ft.Icon(name=ft.icons.PERSON, color="blue"),
            ft.Text(f"Usuario: {self.user_controller.get_state().get('username', 'Invitado')}", 
                   size=16, weight="bold"),
        ], alignment="center")
        
        content = ft.Column([
            self.title,
            ft.Divider(),
            user_info,
            ft.Text("Selecciona la dificultad:", size=18, weight="bold"),
            difficulty_buttons,
            ft.Divider(),
            self.difficulty_text,
            self.mines_counter,
            self.status_message,
            action_buttons,
            self.instructions
        ], alignment="center", horizontal_alignment="center", spacing=20)
        
        self.page.clean()
        self.page.add(content)

    def show_game_page(self, e=None):
        """Muestra el tablero de juego"""
        self.current_page = "game"
        
        if not self.game_controller.current_game:
            self.show_difficulty_selection()
            return
        
        game_state = self.game_controller.get_state()
        
        # Actualizar elementos de UI
        self.difficulty_text.value = f"Dificultad: {self.game_controller.get_difficulty()}"
        self.mines_counter.value = f"Minas: {self.game_controller.get_remaining_mines()}"
        
        # Crear grid de juego usando GridView
        rows = game_state['rows']
        cols = game_state['cols']
        
        # Crear GridView para el tablero
        self.game_grid = ft.GridView(
            expand=1,
            runs_count=cols,  # Número de columnas
            max_extent=35,    # Tamaño máximo de cada celda
            spacing=2,        # Espaciado entre celdas
            run_spacing=2,    # Espaciado entre filas
        )
        
        # Llenar el grid con celdas
        self.update_game_grid()
        
        # Botones de acción
        action_buttons = self.ui.create_action_buttons(
            on_user=lambda e: self.show_login_page(),
            on_stats=lambda e: self.show_stats_dialog(e),
            on_new_game=lambda e: self.show_difficulty_selection(),
            on_exit=lambda e: self.exit_app(e)
        )
        
        user_info = ft.Row([
            ft.Icon(name=ft.icons.PERSON, color="blue"),
            ft.Text(f"Jugando como: {self.user_controller.get_state().get('username', 'Invitado')}", 
                   size=14),
        ], alignment="center")
        
        # Contenedor para el grid con tamaño fijo
        grid_container = ft.Container(
            content=self.game_grid,
            width=cols * 37,  # Ancho basado en número de columnas
            height=rows * 37, # Alto basado en número de filas
            alignment=ft.alignment.center,
            bgcolor="grey100",
            padding=10,
            border_radius=10
        )
        
        content = ft.Column([
            self.title,
            user_info,
            ft.Row([self.difficulty_text, self.mines_counter], alignment="center"),
            self.status_message,
            grid_container,
            action_buttons
        ], alignment="center", horizontal_alignment="center", spacing=15)
        
        self.page.clean()
        self.page.add(content)

    def update_game_grid(self):
        """Actualiza el grid de juego basado en el estado actual"""
        if not self.game_grid or not self.game_controller.current_game:
            return
        
        game_state = self.game_controller.get_state()
        self.game_grid.controls.clear()
        
        for row in range(game_state['rows']):
            for col in range(game_state['cols']):
                cell = self.create_cell(row, col, game_state)
                self.game_grid.controls.append(cell)
        
        self.page.update()

    def create_cell(self, row: int, col: int, game_state: dict):
        """Crea una celda individual basada en su estado"""
        cell = ft.Container(
            width=35,
            height=35,
            alignment=ft.alignment.center,
            border_radius=3,
            on_click=lambda e: self.handle_cell_click(row, col),
            on_long_press=lambda e: self.handle_cell_long_press(row, col),
        )
        
        if game_state['revealed'][row][col]:
            cell.bgcolor = "white"
            cell.border = ft.border.all(1, "grey")
            
            if game_state['board'][row][col] == -1:
                # Mina
                cell.content = ft.Text("💣", size=12)
                cell.bgcolor = "red"
            elif game_state['board'][row][col] > 0:
                # Número
                colors = ["blue", "green", "red", "purple", "maroon", "turquoise", "black", "gray"]
                color = colors[game_state['board'][row][col] - 1] if game_state['board'][row][col] <= len(colors) else "black"
                cell.content = ft.Text(str(game_state['board'][row][col]), size=12, weight="bold", color=color)
            else:
                # Celda vacía
                cell.content = ft.Text("", size=12)
        elif game_state['flagged'][row][col]:
            # Bandera
            cell.bgcolor = "yellow"
            cell.content = ft.Text("🚩", size=12)
        else:
            # Celda no revelada
            cell.bgcolor = "grey300"
            cell.content = ft.Text("", size=12)
        
        return cell

    def handle_login(self, e):
        """Maneja el intento de login"""
        username = self.username_field.value.strip()
        if not username:
            self.message_text.value = "El nombre de usuario es requerido"
            self.message_text.color = "red"
            self.page.update()
            return
        
        success, message = self.user_controller.login(username)
        
        self.message_text.value = message
        self.message_text.color = "green" if success else "red"
        
        if success:
            # Limpiar campos
            self.username_field.value = ""
            self.email_field.value = ""
            self.show_difficulty_selection()
        
        self.page.update()

    def handle_register(self, e):
        """Maneja el intento de registro"""
        username = self.username_field.value.strip()
        email = self.email_field.value.strip()
        
        if not username:
            self.message_text.value = "El nombre de usuario es requerido"
            self.message_text.color = "red"
            self.page.update()
            return
        
        success, message = self.user_controller.register(username, email if email else None)
        
        self.message_text.value = message
        self.message_text.color = "green" if success else "red"
        
        if success:
            # Limpiar campos
            self.username_field.value = ""
            self.email_field.value = ""
            self.show_difficulty_selection()
        
        self.page.update()

    def show_stats_dialog(self, e):
        """Muestra el diálogo de estadísticas"""
        # Obtener estadísticas actualizadas del usuario
        user_stats = self.user_controller.get_state()
        
        if not user_stats or not user_stats.get('username'):
            # Si no hay usuario logueado, mostrar mensaje
            self.status_message.value = "Debes iniciar sesión para ver estadísticas"
            self.status_message.color = "red"
            self.page.update()
            return
        
        # Crear y mostrar el diálogo de estadísticas
        self.stats_dialog = StatsDialog(user_stats, self.close_stats_dialog)
        self.stats_dialog.show(self.page)

    def close_stats_dialog(self, e):
        """Cierra el diálogo de estadísticas"""
        if self.stats_dialog:
            self.stats_dialog.close(self.page)
            self.stats_dialog = None

    def start_game(self, difficulty: str, rows: int, cols: int, mines: int):
        """Inicia un nuevo juego con la dificultad especificada"""
        user_id = self.user_controller.current_user.id if self.user_controller.current_user else None
        self.game_controller.start_new_game(rows, cols, mines, difficulty, user_id)
        
        # Actualizar mensaje de estado
        self.status_message.value = "¡Juego comenzado! Haz click en una celda para empezar."
        self.status_message.color = "blue"
        
        self.show_game_page()

    def handle_cell_click(self, row: int, col: int):
        """Maneja el click en una celda"""
        success, game_ended = self.game_controller.reveal_cell(row, col)
        
        if game_ended:
            if self.game_controller.current_game.game_won:
                self.status_message.value = "¡Felicidades! Has ganado el juego."
                self.status_message.color = "green"
                
                # Actualizar estadísticas del usuario
                if self.user_controller.current_user and self.game_controller.game_start_time:
                    duration = int(time.time() - self.game_controller.game_start_time)
                    self.user_controller.update_user_stats(
                        True, duration, self.game_controller.get_difficulty()
                    )
            else:
                self.status_message.value = "¡Game Over! Has pisado una mina."
                self.status_message.color = "red"
                
                # Actualizar estadísticas del usuario
                if self.user_controller.current_user and self.game_controller.game_start_time:
                    duration = int(time.time() - self.game_controller.game_start_time)
                    self.user_controller.update_user_stats(
                        False, duration, self.game_controller.get_difficulty()
                    )
        
        # Actualizar contador de minas y grid
        if self.game_controller.current_game:
            self.mines_counter.value = f"Minas: {self.game_controller.get_remaining_mines()}"
        self.update_game_grid()

    def handle_cell_long_press(self, row: int, col: int):
        """Maneja el click largo (bandera) en una celda"""
        self.game_controller.toggle_flag(row, col)
        if self.game_controller.current_game:
            self.mines_counter.value = f"Minas: {self.game_controller.get_remaining_mines()}"
        self.update_game_grid()

    def exit_app(self, e):
        """Cierra la aplicación"""
        self.status_message.value = "Para salir, cierre la ventana del navegador"
        self.status_message.color = "orange"
        self.page.update()

def main(page: ft.Page):
    app = MinesweeperApp()
    app.build(page)

if __name__ == "__main__":
    ft.app(target=main)