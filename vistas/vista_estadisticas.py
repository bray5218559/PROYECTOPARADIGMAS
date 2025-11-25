import flet as ft
from typing import Dict, Any, Callable

class VistaEstadisticas:
    def __init__(self):
        pass
    
    def crear_vista_estadisticas(self, estadisticas: Dict[str, Any], al_actualizar: Callable, al_inicio_sesion: Callable):
        """Crea la vista de estadísticas"""
        usuario = estadisticas.get('nombre_usuario', 'Invitado')
        
        return ft.Container(
            content=ft.Column([
                # Encabezado
                ft.Text("Buscaminas", size=24, weight="bold"),
                ft.Row([
                    ft.TextButton("Juego", on_click=lambda e: al_actualizar(e)),
                    ft.TextButton("Estadísticas", on_click=lambda e: None),
                ]),
                ft.Divider(),
                
                # Título de estadísticas
                ft.Text(f"Estadísticas de {usuario}", size=20, weight="bold"),
                ft.Container(height=20),
                
                # Resumen General
                ft.Text("Resumen General", size=18, weight="bold"),
                ft.Container(height=10),
                
                # Estadísticas en tarjetas
                self._crear_tarjetas_estadisticas(estadisticas),
                ft.Container(height=20),
                
                # Porcentaje de victoria
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{estadisticas.get('porcentaje_victorias', 0)}%", 
                               size=24, weight="bold", color="green"),
                        ft.Text("Porcentaje de Victoria", size=14),
                    ], horizontal_alignment="center"),
                    padding=20,
                    border=ft.border.all(1, "grey"),
                    border_radius=8
                ),
                
                ft.Container(height=30),
                ft.Divider(),
                ft.Container(height=20),
                
                # Mejores Tiempos
                ft.Text("Mejores Tiempos", size=18, weight="bold"),
                ft.Container(height=10),
                
                self._crear_tabla_mejores_tiempos(estadisticas),
                
                ft.Container(height=30),
                
                # Botones de acción
                ft.Row([
                    ft.ElevatedButton("Cambiar Usuario", on_click=al_inicio_sesion),
                    ft.ElevatedButton("Volver al Juego", on_click=al_actualizar),
                ], alignment="center", spacing=20)
                
            ], scroll="adaptive"),
            padding=20
        )
    
    def _crear_tarjetas_estadisticas(self, estadisticas: Dict[str, Any]):
        """Crea las tarjetas con las estadísticas principales"""
        partidas_totales = estadisticas.get('partidas_totales', 0)
        partidas_ganadas = estadisticas.get('partidas_ganadas', 0)
        partidas_perdidas = estadisticas.get('partidas_perdidas', 0)
        
        return ft.Row([
            # Partidas Totales
            ft.Container(
                content=ft.Column([
                    ft.Text(str(partidas_totales), size=24, weight="bold", color="blue"),
                    ft.Text("Partidas Totales", size=14),
                ], horizontal_alignment="center"),
                padding=20,
                border=ft.border.all(1, "grey"),
                border_radius=8,
                expand=True
            ),
            
            ft.Container(width=10),
            
            # Partidas Ganadas
            ft.Container(
                content=ft.Column([
                    ft.Text(str(partidas_ganadas), size=24, weight="bold", color="green"),
                    ft.Text("Partidas Ganadas", size=14),
                ], horizontal_alignment="center"),
                padding=20,
                border=ft.border.all(1, "grey"),
                border_radius=8,
                expand=True
            ),
            
            ft.Container(width=10),
            
            # Partidas Perdidas
            ft.Container(
                content=ft.Column([
                    ft.Text(str(partidas_perdidas), size=24, weight="bold", color="red"),
                    ft.Text("Partidas Perdidas", size=14),
                ], horizontal_alignment="center"),
                padding=20,
                border=ft.border.all(1, "grey"),
                border_radius=8,
                expand=True
            ),
        ])
    
    def _crear_tabla_mejores_tiempos(self, estadisticas: Dict[str, Any]):
        """Crea la tabla de mejores tiempos por dificultad"""
        mejores_tiempos = estadisticas.get('mejores_tiempos', {})
        
        return ft.Column([
            # Fácil
            ft.Row([
                ft.Text("Fácil:", weight="bold", width=80),
                ft.Text(f"{mejores_tiempos.get('facil', 'N/A')} segundos", width=150),
            ]),
            ft.Container(height=5),
            
            # Medio
            ft.Row([
                ft.Text("Medio:", weight="bold", width=80),
                ft.Text(f"{mejores_tiempos.get('medio', 'N/A')} segundos", width=150),
            ]),
            ft.Container(height=5),
            
            # Difícil
            ft.Row([
                ft.Text("Difícil:", weight="bold", width=80),
                ft.Text(f"{mejores_tiempos.get('dificil', 'N/A')} segundos", width=150),
            ]),
        ])