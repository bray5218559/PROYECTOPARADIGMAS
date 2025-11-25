# vistas/ui_components.py
import flet as ft
from typing import Callable, Optional, Dict, Any

class BaseDialog:
    """Clase base para diálogos"""
    def __init__(self):
        self.dialog = None
    
    def show(self, page: ft.Page):
        if self.dialog:
            page.dialog = self.dialog
            self.dialog.open = True
            page.update()
    
    def close(self, page: ft.Page):
        if self.dialog:
            self.dialog.open = False
            page.update()

class UserDialog(BaseDialog):
    def __init__(self, on_login: Callable, on_register: Callable, on_close: Callable):
        super().__init__()
        self.username_field = ft.TextField(label="Nombre de usuario", width=300)
        self.email_field = ft.TextField(label="Email (opcional)", width=300)
        self.message_text = ft.Text("", color="red", size=12)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text("Iniciar Sesión / Registrarse"),
            content=ft.Column([
                self.username_field,
                self.email_field,
                self.message_text
            ], tight=True),
            actions=[
                ft.TextButton("Iniciar Sesión", on_click=on_login),
                ft.TextButton("Registrarse", on_click=on_register),
                ft.TextButton("Cerrar", on_click=on_close)
            ],
            actions_alignment="end"
        )
    
    def get_username(self) -> str:
        return self.username_field.value or ""
    
    def get_email(self) -> str:
        return self.email_field.value or ""
    
    def set_message(self, message: str, is_error: bool = True):
        self.message_text.value = message
        self.message_text.color = "red" if is_error else "green"

class StatsDialog(BaseDialog):
    def __init__(self, user_data: Dict[str, Any], on_close: Callable):
        super().__init__()
        
        # Calcular partidas perdidas
        total_games = user_data.get('total_games', 0)
        games_won = user_data.get('games_won', 0)
        games_lost = total_games - games_won
        
        # Crear contenido de estadísticas
        content = []
        if user_data and user_data.get('username'):
            # Encabezado con nombre de usuario
            content.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(name="person", color="blue", size=24),
                        ft.Text(f"{user_data['username']}", size=20, weight="bold")
                    ]),
                    padding=5,
                    margin=5
                )
            )
            
            # Estadísticas principales
            content.extend([
                ft.Divider(),
                ft.Text("ESTADÍSTICAS GENERALES", size=16, weight="bold", color="blue"),
                
                # Partidas totales, ganadas y perdidas
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name="sports_esports", color="blue"),
                            ft.Text(f"Partidas totales: {total_games}", size=14, weight="bold")
                        ]),
                        ft.Row([
                            ft.Icon(name="emoji_events", color="green"),
                            ft.Text(f"Partidas ganadas: {games_won}", size=14, weight="bold", color="green")
                        ]),
                        ft.Row([
                            ft.Icon(name="mood_bad", color="red"),
                            ft.Text(f"Partidas perdidas: {games_lost}", size=14, weight="bold", color="red")
                        ])
                    ], spacing=5),
                    padding=10,
                    bgcolor="grey100",
                    border_radius=10,
                    margin=5
                ),
                
                # Porcentaje de victorias
                ft.Container(
                    content=ft.Column([
                        ft.Text("EFECTIVIDAD", size=14, weight="bold"),
                        ft.Text(f"{user_data.get('win_percentage', 0):.1f}% de victorias", 
                               size=16, weight="bold", 
                               color="green" if user_data.get('win_percentage', 0) > 50 else "orange")
                    ], horizontal_alignment="center"),
                    padding=10,
                    bgcolor="blue50",
                    border_radius=10,
                    margin=5
                ),
                
                ft.Divider(),
                ft.Text("MEJORES TIEMPOS", size=16, weight="bold", color="blue"),
                
                # Mejores tiempos por dificultad
                ft.Container(
                    content=ft.Column([
                        self._create_time_row("Fácil", user_data.get('best_time_easy'), "🟢"),
                        self._create_time_row("Medio", user_data.get('best_time_medium'), "🟡"),
                        self._create_time_row("Difícil", user_data.get('best_time_hard'), "🔴")
                    ]),
                    padding=10,
                    bgcolor="grey50",
                    border_radius=10,
                    margin=5
                )
            ])
        else:
            content = [
                ft.Text("No hay datos de estadísticas disponibles", size=14),
                ft.Text("Juega algunas partidas para ver tus estadísticas", size=12, color="grey")
            ]
        
        self.dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(name="leaderboard", color="blue"),
                ft.Text("Estadísticas del Jugador")
            ]),
            content=ft.Column(content, scroll="adaptive"),
            actions=[ft.TextButton("Cerrar", on_click=on_close)],
        )
    
    def _create_time_row(self, difficulty: str, time_value: Any, emoji: str):
        """Crea una fila para mostrar el mejor tiempo de una dificultad"""
        time_text = f"{time_value} segundos" if time_value is not None else "No registrado"
        color = "green" if time_value is not None else "gray"
        
        return ft.Row([
            ft.Text(emoji, size=16),
            ft.Text(f"{difficulty}:", size=14, weight="bold", width=80),
            ft.Text(time_text, size=14, color=color)
        ])

class UIComponents:
    @staticmethod
    def create_title():
        return ft.Text("BUSCAMINAS", size=32, weight="bold", color="blue900")

    @staticmethod
    def create_difficulty_text():
        return ft.Text("Dificultad: Fácil", size=16, weight="bold")

    @staticmethod
    def create_mines_counter():
        return ft.Text("Minas: 0", size=16, weight="bold")

    @staticmethod
    def create_status_message():
        return ft.Text("¡Bienvenido! Selecciona una dificultad para comenzar.", 
                      size=16, weight="bold", color="blue")

    @staticmethod
    def create_game_grid(rows: int, cols: int, on_cell_click: Callable, on_cell_long_press: Callable):
        return ft.GridView(
            expand=1,
            runs_count=cols,
            max_extent=35,
            spacing=2,
            run_spacing=2,
        )

    @staticmethod
    def create_cell_button(row: int, col: int, on_click: Callable, on_long_press: Callable):
        return ft.Container(
            content=ft.Text("", size=12, weight="bold"),
            width=35,
            height=35,
            alignment=ft.alignment.center,
            bgcolor="grey300",
            border_radius=3,
            on_click=lambda e: on_click(row, col),
            on_long_press=lambda e: on_long_press(row, col),
        )

    @staticmethod
    def create_difficulty_buttons(on_easy: Callable, on_medium: Callable, on_hard: Callable):
        return ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Fácil (8x8 - 10 minas)", 
                    on_click=on_easy, 
                    bgcolor="green400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Medio (12x12 - 30 minas)", 
                    on_click=on_medium, 
                    bgcolor="orange400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Difícil (16x16 - 60 minas)", 
                    on_click=on_hard, 
                    bgcolor="red400", 
                    color="white"
                ),
            ],
            alignment="center",
            spacing=10,
        )

    @staticmethod
    def create_action_buttons(on_user: Callable, on_stats: Callable, on_new_game: Callable, on_exit: Callable):
        return ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Usuario", 
                    icon="person", 
                    on_click=on_user,
                    bgcolor="blue400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Estadísticas", 
                    icon="leaderboard", 
                    on_click=on_stats,
                    bgcolor="green400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Nuevo Juego", 
                    icon="replay", 
                    on_click=on_new_game,
                    bgcolor="blue400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Salir", 
                    icon="exit_to_app", 
                    on_click=on_exit,
                    bgcolor="red400", 
                    color="white"
                ),
            ],
            alignment="center",
            spacing=10,
        )

    @staticmethod
    def create_instructions():
        return ft.Container(
            content=ft.Column([
                ft.Text("Instrucciones:", weight="bold"),
                ft.Text("• Click izquierdo: Revelar celda"),
                ft.Text("• Click largo o derecho: Colocar/remover bandera"),
                ft.Text("• Objetivo: Revelar todas las celdas sin minas"),
            ], spacing=5),
            padding=10,
            bgcolor="grey100",
            border_radius=10,
            margin=10,
        )