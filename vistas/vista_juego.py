# vistas/vista_juego.py
import flet as ft
from typing import Callable, Dict, Any
from vistas.componentes_ui import FabricaComponentesUI

class VistaJuego:
    """Vista responsable de mostrar el tablero de juego y elementos relacionados"""
    
    def __init__(self):
        self.fabrica = FabricaComponentesUI()
        self.titulo = self.fabrica.crear_titulo()
        self.texto_dificultad = self.fabrica.crear_texto_dificultad()
        self.contador_minas = self.fabrica.crear_contador_minas()
        self.mensaje_estado = self.fabrica.crear_mensaje_estado()
        self.grid_juego = None

    def crear_vista_seleccion_dificultad(self, 
                                       al_facil: Callable, 
                                       al_medio: Callable, 
                                       al_dificil: Callable,
                                       al_usuario: Callable,
                                       al_estadisticas: Callable,
                                       al_nuevo_juego: Callable,
                                       al_salir: Callable) -> ft.Column:
        """Crea la vista de selección de dificultad"""
        return ft.Column([
            ft.Text("Selección de Dificultad", size=20, weight="bold"),
            self.fabrica.crear_botones_dificultad(al_facil, al_medio, al_dificil),
            ft.Divider(),
            self.texto_dificultad,
            self.contador_minas,
            self.mensaje_estado,
            ft.Container(content=ft.Text("Selecciona una dificultad para comenzar", size=16, color="gray")),
            self.fabrica.crear_botones_accion(al_usuario, al_estadisticas, al_nuevo_juego, al_salir),
            self.fabrica.crear_instrucciones()
        ], alignment="center", horizontal_alignment="center", spacing=15)

    def crear_vista_tablero_juego(self, 
                                estado_juego: Dict[str, Any], 
                                nombre_usuario: str,
                                al_click_celda: Callable,
                                al_presion_larga_celda: Callable,
                                al_usuario: Callable,
                                al_estadisticas: Callable,
                                al_nuevo_juego: Callable,
                                al_salir: Callable) -> ft.Column:
        """Crea la vista del tablero de juego en curso"""
        
        # Actualizar elementos de UI
        self.contador_minas.value = f"Minas: {self._calcular_minas_restantes(estado_juego)}"
        
        # Crear grid de juego
        grid_juego = self._crear_grid_juego(estado_juego, al_click_celda, al_presion_larga_celda)
        
        info_usuario = ft.Row([
            ft.Icon(ft.Icons.PERSON, color="blue"),
            ft.Text(f"Jugando como: {nombre_usuario}", size=14),
        ], alignment="center")
        
        return ft.Column([
            info_usuario,
            ft.Row([self.texto_dificultad, self.contador_minas], alignment="center"),
            self.mensaje_estado,
            ft.Container(content=grid_juego, padding=10),
            self.fabrica.crear_botones_accion(al_usuario, al_estadisticas, al_nuevo_juego, al_salir)
        ], alignment="center", horizontal_alignment="center", spacing=15)

    def _crear_grid_juego(self, estado_juego: Dict[str, Any], al_click_celda: Callable, al_presion_larga_celda: Callable) -> ft.Column:
        """Crea el grid de juego basado en el estado actual"""
        filas = estado_juego['filas']
        columnas = estado_juego['columnas']
        
        controles_grid = []
        for fila in range(filas):
            controles_fila = []
            for columna in range(columnas):
                celda = self._crear_celda(fila, columna, estado_juego, al_click_celda, al_presion_larga_celda)
                controles_fila.append(celda)
            
            fila_grid = ft.Row(controls=controles_fila, alignment="center")
            controles_grid.append(fila_grid)
        
        return ft.Column(controls=controles_grid, spacing=2)

    def _crear_celda(self, fila: int, columna: int, estado_juego: Dict[str, Any], al_click: Callable, al_presion_larga: Callable) -> ft.Container:
        """Crea una celda individual basada en su estado"""
        celda = ft.Container(
            width=35,
            height=35,
            alignment=ft.alignment.center,
            border_radius=3,
            on_click=lambda e: al_click(fila, columna),
            on_long_press=lambda e: al_presion_larga(fila, columna),
        )
        
        if estado_juego['revelado'][fila][columna]:
            celda.bgcolor = "white"
            celda.border = ft.border.all(1, "grey")
            
            if estado_juego['tablero'][fila][columna] == -1:
                # Mina
                celda.content = ft.Text("💣", size=12)
                celda.bgcolor = "red"
            elif estado_juego['tablero'][fila][columna] > 0:
                # Número
                colores = ["blue", "green", "red", "purple", "maroon", "turquoise", "black", "gray"]
                color = colores[estado_juego['tablero'][fila][columna] - 1] if estado_juego['tablero'][fila][columna] <= len(colores) else "black"
                celda.content = ft.Text(str(estado_juego['tablero'][fila][columna]), size=12, weight="bold", color=color)
            else:
                # Celda vacía
                celda.content = ft.Text("", size=12)
        elif estado_juego['banderas'][fila][columna]:
            # Bandera
            celda.bgcolor = "yellow"
            celda.content = ft.Text("🚩", size=12)
        else:
            # Celda no revelada
            celda.bgcolor = "grey300"
            celda.content = ft.Text("", size=12)
        
        return celda

    def _calcular_minas_restantes(self, estado_juego: Dict[str, Any]) -> int:
        """Calcula minas restantes basado en banderas"""
        contador_banderas = sum(sum(1 for celda in fila if celda) for fila in estado_juego['banderas'])
        return estado_juego['minas'] - contador_banderas

    def actualizar_dificultad(self, dificultad: str):
        """Actualiza el texto de dificultad"""
        self.texto_dificultad.value = f"Dificultad: {dificultad}"

    def actualizar_mensaje_estado(self, mensaje: str, color: str = "blue"):
        """Actualiza el mensaje de estado"""
        self.mensaje_estado.value = mensaje
        self.mensaje_estado.color = color

    def actualizar_contador_minas(self, minas_restantes: int):
        """Actualiza el contador de minas"""
        self.contador_minas.value = f"Minas: {minas_restantes}"