# vistas/ui_components.py
import flet as ft
from typing import Callable, Optional

class UIComponents:
    @staticmethod
    def create_title():
        return ft.Text("BUSCAMINAS", size=32, weight="bold", color="blue900")

    @staticmethod
    def create_difficulty_text():
        return ft.Text("Dificultad: Fácil", size=16)

    @staticmethod
    def create_mines_counter():
        return ft.Text("Minas: 0", size=16, weight="bold")

    @staticmethod
    def create_status_message():
        return ft.Text("", size=18, weight="bold")

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
            content=ft.Text("", size=12),
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
    def create_action_buttons(on_continue: Callable, on_exit: Callable, on_user: Callable, on_stats: Callable):
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
                    "Continuar", 
                    icon="replay", 
                    on_click=on_continue,
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

    @staticmethod
    def create_user_dialog(on_login: Callable, on_register: Callable, on_close: Optional[Callable] = None):
        # Función local para cerrar el diálogo
        def default_close(e):
            # Esta función se manejará en main.py
            pass
            
        dialog = ft.AlertDialog(
            title=ft.Text("Iniciar Sesión / Registrarse"),
            content=ft.Column([
                ft.TextField(label="Nombre de usuario", width=300),
                ft.TextField(label="Email (opcional)", width=300),
                ft.Text("", color="red", size=12)
            ], tight=True),
            actions=[
                ft.TextButton("Iniciar Sesión", on_click=on_login),
                ft.TextButton("Registrarse", on_click=on_register),
                ft.TextButton("Cerrar", on_click=on_close if on_close else default_close)
            ],
            actions_alignment="end"
        )
        return dialog

    @staticmethod
    def create_stats_dialog(user_data: dict, on_close: Callable):
        return ft.AlertDialog(
            title=ft.Text(f"Estadísticas de {user_data['username']}"),
            content=ft.Column([
                ft.Text(f"Partidas totales: {user_data['total_games']}"),
                ft.Text(f"Partidas ganadas: {user_data['games_won']}"),
                ft.Text(f"Porcentaje de victorias: {user_data['win_percentage']:.1f}%"),
                ft.Text(f"Mejor tiempo (Fácil): {user_data['best_time_easy'] or 'N/A'} segundos"),
                ft.Text(f"Mejor tiempo (Medio): {user_data['best_time_medium'] or 'N/A'} segundos"),
                ft.Text(f"Mejor tiempo (Difícil): {user_data['best_time_hard'] or 'N/A'} segundos"),
            ]),
            actions=[ft.TextButton("Cerrar", on_click=on_close)],
        )