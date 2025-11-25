# vistas/vista_estadisticas.py
import flet as ft
from typing import Dict, Any, Callable
from vistas.componentes_ui import FabricaComponentesUI

class VistaEstadisticas:
    """Vista responsable de mostrar las estadísticas del juego"""
    
    def __init__(self):
        self.fabrica = FabricaComponentesUI()

    def crear_vista_estadisticas(self, 
                               estadisticas: Dict[str, Any],
                               al_actualizar: Callable,
                               al_inicio_sesion: Callable) -> ft.Column:
        """Crea la vista de estadísticas"""
        
        if not estadisticas or not estadisticas.get('nombre_usuario'):
            return self._crear_vista_sin_estadisticas(al_inicio_sesion)
        else:
            return self._crear_vista_con_estadisticas(estadisticas, al_actualizar)

    def _crear_vista_sin_estadisticas(self, al_inicio_sesion: Callable) -> ft.Column:
        """Crea vista cuando no hay estadísticas disponibles"""
        return ft.Column([
            ft.Icon(ft.Icons.WARNING, size=48, color="orange"),
            ft.Text("Debes iniciar sesión", size=18, weight="bold"),
            ft.Text("Inicia sesión para ver tus estadísticas", size=14, color="gray"),
            ft.ElevatedButton(
                "Ir a Inicio de Sesión",
                icon=ft.Icons.LOGIN,
                on_click=al_inicio_sesion,
                bgcolor="blue400",
                color="white"
            )
        ], alignment="center", horizontal_alignment="center", spacing=15)

    def _crear_vista_con_estadisticas(self, estadisticas: Dict[str, Any], al_actualizar: Callable) -> ft.Column:
        """Crea vista con estadísticas del usuario"""
        
        # Tarjeta de resumen general
        tarjeta_resumen = self._crear_tarjeta_resumen(estadisticas)
        
        # Tarjeta de mejores tiempos
        tarjeta_tiempos = self._crear_tarjeta_tiempos(estadisticas)
        
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PERSON, color="blue", size=24),
                ft.Text(f"Estadísticas de {estadisticas['nombre_usuario']}", 
                       size=22, weight="bold", color="blue")
            ], alignment="center"),
            tarjeta_resumen,
            tarjeta_tiempos,
            ft.ElevatedButton(
                "Actualizar Estadísticas",
                icon=ft.Icons.REFRESH,
                on_click=al_actualizar,
                bgcolor="blue400",
                color="white"
            )
        ], spacing=20)

    def _crear_tarjeta_resumen(self, estadisticas: Dict[str, Any]) -> ft.Card:
        """Crea la tarjeta de resumen general"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Resumen General", size=20, weight="bold", color="blue"),
                    ft.Divider(),
                    ft.Row([
                        self._crear_elemento_estadistica("Partidas Totales", 
                                                       estadisticas['partidas_totales'], 
                                                       ft.Icons.SPORTS_ESPORTS),
                        self._crear_elemento_estadistica("Partidas Ganadas", 
                                                       estadisticas['partidas_ganadas'], 
                                                       ft.Icons.EMOJI_EVENTS),
                        self._crear_elemento_estadistica("Partidas Perdidas", 
                                                       estadisticas['partidas_perdidas'], 
                                                       ft.Icons.MOOD_BAD),
                    ], alignment="space_around"),
                    ft.Container(
                        content=ft.Row([
                            self._crear_elemento_estadistica("Porcentaje de Victoria", 
                                                           f"{estadisticas['porcentaje_victorias']}%", 
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

    def _crear_tarjeta_tiempos(self, estadisticas: Dict[str, Any]) -> ft.Card:
        """Crea la tarjeta de mejores tiempos"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Mejores Tiempos", size=20, weight="bold", color="green"),
                    ft.Divider(),
                    ft.Row([
                        self._crear_elemento_tiempo("Fácil", estadisticas.get('mejor_tiempo_facil'), "🟢"),
                        self._crear_elemento_tiempo("Medio", estadisticas.get('mejor_tiempo_medio'), "🟡"),
                        self._crear_elemento_tiempo("Difícil", estadisticas.get('mejor_tiempo_dificil'), "🔴"),
                    ], alignment="space_around")
                ], spacing=15),
                padding=20
            ),
            elevation=5,
            margin=10
        )

    def _crear_elemento_estadistica(self, etiqueta: str, valor, icono) -> ft.Column:
        """Crea un elemento de estadística individual"""
        return ft.Column([
            ft.Icon(icono, size=30, color="blue"),
            ft.Text(str(valor), size=24, weight="bold"),
            ft.Text(etiqueta, size=12, color="gray", text_align="center")
        ], horizontal_alignment="center", spacing=5)

    def _crear_elemento_tiempo(self, dificultad: str, valor_tiempo, emoji: str) -> ft.Column:
        """Crea un elemento de tiempo individual"""
        tiempo_mostrar = f"{valor_tiempo}s" if valor_tiempo else "No registrado"
        color = "green" if dificultad == "Fácil" else "orange" if dificultad == "Medio" else "red"
        
        return ft.Column([
            ft.Text(emoji, size=30),
            ft.Text(dificultad, size=14, weight="bold", color=color),
            ft.Text(tiempo_mostrar, size=16, weight="bold"),
            ft.Text("mejor tiempo", size=10, color="gray")
        ], horizontal_alignment="center", spacing=5)