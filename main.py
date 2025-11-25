# main.py
import flet as ft
import time
import sys
from modelos.json_database import JSONDatabase, UserDAO, GameDAO
from controladores.user_controller import UserController
from controladores.game_controller import GameController
from vistas.ui_components import UIComponents

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
        
        # Elementos de UI
        self.title = self.ui.create_title()
        self.difficulty_text = self.ui.create_difficulty_text()
        self.mines_counter = self.ui.create_mines_counter()
        self.status_message = self.ui.create_status_message()
        self.game_grid = None
        self.instructions = self.ui.create_instructions()
        
        # Referencias para contenido dinámico
        self.game_content_ref = ft.Ref[ft.Container]()
        
        # Estados
        self.current_page = "login"
        self.tabs = None
        self.main_content = None

    def build(self, page: ft.Page):
        self.page = page
        page.title = "Buscaminas"
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"
        page.theme_mode = "light"
        page.padding = 20
        
        # Mostrar página de login inicialmente
        self.show_login_page()

    def create_main_layout(self):
        """Crea el layout principal con pestañas"""
        # Crear las pestañas
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Juego",
                    content=ft.Container(ref=self.game_content_ref)
                ),
                ft.Tab(
                    text="Estadísticas",
                    content=self.create_stats_content()
                ),
            ],
            on_change=self.on_tab_change
        )
        
        # Layout principal
        self.main_content = ft.Column([
            self.title,
            ft.Divider(),
            self.tabs
        ])

    def update_game_content(self):
        """Actualiza el contenido de la pestaña de juego"""
        if not self.game_controller.current_game:
            # Mostrar selección de dificultad
            content = ft.Column([
                ft.Text("Selección de Dificultad", size=20, weight="bold"),
                self.ui.create_difficulty_buttons(
                    on_easy=lambda e: self.start_game("Fácil", 8, 8, 10),
                    on_medium=lambda e: self.start_game("Medio", 12, 12, 30),
                    on_hard=lambda e: self.start_game("Difícil", 16, 16, 60)
                ),
                ft.Divider(),
                self.difficulty_text,
                self.mines_counter,
                self.status_message,
                ft.Container(content=ft.Text("Selecciona una dificultad para comenzar", size=16, color="gray")),
                self.ui.create_action_buttons(
                    on_user=lambda e: self.show_login_page(),
                    on_stats=lambda e: self.show_stats_tab(),
                    on_new_game=lambda e: self.show_difficulty_selection(),
                    on_exit=lambda e: self.exit_app(e)
                ),
                self.instructions
            ], alignment="center", horizontal_alignment="center", spacing=15)
        else:
            # Mostrar juego en curso
            game_state = self.game_controller.get_state()
            
            # Actualizar elementos de UI
            self.difficulty_text.value = f"Dificultad: {self.game_controller.get_difficulty()}"
            self.mines_counter.value = f"Minas: {self.game_controller.get_remaining_mines()}"
            
            # Crear grid de juego
            self.create_game_grid_directly(game_state)
            
            user_info = ft.Row([
                ft.Icon(ft.Icons.PERSON, color="blue"),
                ft.Text(f"Jugando como: {self.user_controller.get_state().get('username', 'Invitado')}", 
                       size=14),
            ], alignment="center")
            
            content = ft.Column([
                user_info,
                ft.Row([self.difficulty_text, self.mines_counter], alignment="center"),
                self.status_message,
                ft.Container(content=self.game_grid, padding=10),
                self.ui.create_action_buttons(
                    on_user=lambda e: self.show_login_page(),
                    on_stats=lambda e: self.show_stats_tab(),
                    on_new_game=lambda e: self.show_difficulty_selection(),
                    on_exit=lambda e: self.exit_app(e)
                )
            ], alignment="center", horizontal_alignment="center", spacing=15)
        
        # Actualizar el contenido de la pestaña de juego
        self.game_content_ref.current.content = content
        self.page.update()

    def create_game_grid_directly(self, game_state: dict):
        """Crea el grid de juego directamente sin depender de UIComponents"""
        rows = game_state['rows']
        cols = game_state['cols']
        
        # Crear un grid de contenedores
        grid_controls = []
        for row in range(rows):
            row_controls = []
            for col in range(cols):
                cell = self.create_cell(row, col, game_state)
                row_controls.append(cell)
            
            # Crear una fila con las celdas
            grid_row = ft.Row(controls=row_controls, alignment="center")
            grid_controls.append(grid_row)
        
        # Crear el grid como una columna de filas
        self.game_grid = ft.Column(controls=grid_controls, spacing=2)

    def create_stats_content(self):
        """Crea el contenido de la pestaña de estadísticas"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Estadísticas de Juego", size=24, weight="bold", color="blue"),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Inicia sesión para ver tus estadísticas", 
                               size=16, color="gray", italic=True)
                    ], alignment="center", horizontal_alignment="center"),
                    padding=20,
                    margin=10
                )
            ], alignment="start", spacing=20),
            padding=20
        )

    def on_tab_change(self, e):
        """Maneja el cambio de pestañas"""
        if self.tabs.selected_index == 0:  # Pestaña de Juego
            self.update_game_content()
        elif self.tabs.selected_index == 1:  # Pestaña de Estadísticas
            self.update_stats_tab()

    def update_stats_tab(self):
        """Actualiza el contenido de la pestaña de estadísticas"""
        # Verificar si hay usuario logueado
        if not self.user_controller.current_user:
            content = ft.Column([
                ft.Icon(ft.Icons.WARNING, size=48, color="orange"),
                ft.Text("Debes iniciar sesión", size=18, weight="bold"),
                ft.Text("Inicia sesión para ver tus estadísticas", size=14, color="gray"),
                ft.ElevatedButton(
                    "Ir a Inicio de Sesión",
                    icon=ft.Icons.LOGIN,
                    on_click=lambda e: self.show_login_page(),
                    bgcolor="blue400",
                    color="white"
                )
            ], alignment="center", horizontal_alignment="center", spacing=15)
        else:
            # Obtener estadísticas actualizadas
            user_stats = self.user_controller.get_state()
            
            if not user_stats or not user_stats.get('username'):
                content = ft.Column([
                    ft.Icon(ft.Icons.INFO, size=48, color="blue"),
                    ft.Text("No hay datos disponibles", size=18, weight="bold"),
                    ft.Text("Juega algunas partidas para generar estadísticas", size=14, color="gray")
                ], alignment="center", horizontal_alignment="center", spacing=15)
            else:
                # Crear interfaz de estadísticas
                content = self.create_stats_interface(user_stats)
        
        # Actualizar el contenido de la pestaña de estadísticas
        stats_tab = self.tabs.tabs[1]
        stats_tab.content.content = content
        self.page.update()

    def create_stats_interface(self, stats: dict):
        """Crea la interfaz de estadísticas con los datos del usuario"""
        # Tarjeta de resumen general
        summary_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Resumen General", size=20, weight="bold", color="blue"),
                    ft.Divider(),
                    ft.Row([
                        self.create_stat_item("Partidas Totales", stats['total_games'], ft.Icons.SPORTS_ESPORTS),
                        self.create_stat_item("Partidas Ganadas", stats['games_won'], ft.Icons.EMOJI_EVENTS),
                        self.create_stat_item("Partidas Perdidas", stats['games_lost'], ft.Icons.MOOD_BAD),
                    ], alignment="space_around"),
                    ft.Container(
                        content=ft.Row([
                            self.create_stat_item("Porcentaje de Victoria", 
                                                f"{stats['win_percentage']}%", 
                                                ft.Icons.TRENDING_UP)
                        ], alignment="center"),
                        margin=ft.margin.only(top=10)
                    )
                ], spacing=15),
                padding=20
            ),
            elevation=5,
            margin=10
        )
        
        # Tarjeta de mejores tiempos
        times_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Mejores Tiempos", size=20, weight="bold", color="green"),
                    ft.Divider(),
                    ft.Row([
                        self.create_time_item("Fácil", stats.get('best_time_easy'), "🟢"),
                        self.create_time_item("Medio", stats.get('best_time_medium'), "🟡"),
                        self.create_time_item("Difícil", stats.get('best_time_hard'), "🔴"),
                    ], alignment="space_around")
                ], spacing=15),
                padding=20
            ),
            elevation=5,
            margin=10
        )
        
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PERSON, color="blue", size=24),
                ft.Text(f"Estadísticas de {stats['username']}", 
                       size=22, weight="bold", color="blue")
            ], alignment="center"),
            summary_card,
            times_card,
            ft.ElevatedButton(
                "Actualizar Estadísticas",
                icon=ft.Icons.REFRESH,
                on_click=lambda e: self.update_stats_tab(),
                bgcolor="blue400",
                color="white"
            )
        ], spacing=20)

    def create_stat_item(self, label: str, value, icon):
        """Crea un elemento de estadística individual"""
        return ft.Column([
            ft.Icon(icon, size=30, color="blue"),
            ft.Text(str(value), size=24, weight="bold"),
            ft.Text(label, size=12, color="gray", text_align="center")
        ], horizontal_alignment="center", spacing=5)

    def create_time_item(self, difficulty: str, time_value, emoji: str):
        """Crea un elemento de tiempo individual"""
        time_display = f"{time_value}s" if time_value else "No registrado"
        color = "green" if difficulty == "Fácil" else "orange" if difficulty == "Medio" else "red"
        
        return ft.Column([
            ft.Text(emoji, size=30),
            ft.Text(difficulty, size=14, weight="bold", color=color),
            ft.Text(time_display, size=16, weight="bold"),
            ft.Text("mejor tiempo", size=10, color="gray")
        ], horizontal_alignment="center", spacing=5)

    def show_stats_tab(self):
        """Muestra la pestaña de estadísticas"""
        if not self.main_content:
            self.create_main_layout()
        
        self.tabs.selected_index = 1
        self.update_stats_tab()
        self.page.update()

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
                    icon=ft.Icons.LOGIN,
                    on_click=self.handle_login,
                    bgcolor="blue400",
                    color="white",
                    width=150
                ),
                ft.ElevatedButton(
                    "Registrarse",
                    icon=ft.Icons.PERSON_ADD,
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
        
        # Crear layout principal si no existe
        if not self.main_content:
            self.create_main_layout()
        
        # Resetear el juego
        self.game_controller.current_game = None
        self.game_grid = None
        self.status_message.value = "Selecciona una dificultad para comenzar"
        self.status_message.color = "blue"
        
        self.page.clean()
        self.page.add(self.main_content)
        self.tabs.selected_index = 0
        self.update_game_content()

    def show_game_page(self, e=None):
        """Muestra el tablero de juego"""
        self.current_page = "game"
        
        if not self.game_controller.current_game:
            self.show_difficulty_selection()
            return
        
        # Crear layout principal si no existe
        if not self.main_content:
            self.create_main_layout()
        
        self.page.clean()
        self.page.add(self.main_content)
        self.tabs.selected_index = 0
        self.update_game_content()

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
        self.update_game_content()

    def handle_cell_long_press(self, row: int, col: int):
        """Maneja el click largo (bandera) en una celda"""
        self.game_controller.toggle_flag(row, col)
        if self.game_controller.current_game:
            self.mines_counter.value = f"Minas: {self.game_controller.get_remaining_mines()}"
        self.update_game_content()

    def exit_app(self, e):
        """Cierra la aplicación"""
        # Método simplificado - muestra mensaje en lugar de cerrar
        if hasattr(self, 'status_message'):
            self.status_message.value = "Para salir, cierre la ventana del navegador"
            self.status_message.color = "orange"
            self.page.update()

    def _show_message(self, message: str, color: str):
        """Muestra un mensaje en la interfaz"""
        if self.current_page == "game":
            self.status_message.value = message
            self.status_message.color = color
            self.page.update()
        elif self.current_page == "difficulty" and hasattr(self, 'message_text'):
            self.message_text.value = message
            self.message_text.color = color
            self.page.update()

def main(page: ft.Page):
    app = MinesweeperApp()
    app.build(page)

if __name__ == "__main__":
    ft.app(target=main)