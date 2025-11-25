import flet as ft
from typing import Callable, Dict, Any

class VistaJuego:
    def __init__(self):
        self.titulo = ft.Text("Buscaminas", size=24, weight="bold")
        self.mensaje_estado = ft.Text("Selecciona una dificultad para comenzar", size=16)
        self.contador_minas = ft.Text("Minas: 0", size=16, weight="bold")
        self.dificultad_actual = ft.Text("Dificultad: No seleccionada", size=14)
        
    def crear_vista_seleccion_dificultad(self, al_facil, al_medio, al_dificil, al_usuario, al_estadisticas, al_nuevo_juego, al_salir):
        """Crea la vista de selección de dificultad"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Buscaminas", size=24, weight="bold"),
                ft.Row([
                    ft.TextButton("Juego", on_click=lambda e: None),
                    ft.TextButton("Estadísticas", on_click=al_estadisticas),
                ]),
                ft.Divider(),
                
                ft.Container(height=20),
                
                # Botones de dificultad
                ft.ElevatedButton(
                    "Fácil (8x8 - 10 minas)",
                    on_click=al_facil,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="green"
                    ),
                    width=200
                ),
                
                ft.Container(height=10),
                
                ft.ElevatedButton(
                    "Medio (12x12 - 30 minas)", 
                    on_click=al_medio,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="orange"
                    ),
                    width=200
                ),
                
                ft.Container(height=10),
                
                ft.ElevatedButton(
                    "Difícil (16x16 - 60 minas)",
                    on_click=al_dificil, 
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="red"
                    ),
                    width=200
                ),
                
                ft.Container(height=30),
                
                # Mensaje de estado
                self.mensaje_estado,
                
                ft.Container(height=20),
                
                # Botones de acción
                ft.Row([
                    ft.ElevatedButton("Continuar", on_click=al_facil),
                    ft.ElevatedButton("Salir del Juego", on_click=al_salir),
                ], alignment="center", spacing=20)
                
            ], horizontal_alignment="center"),
            padding=20,
            alignment=ft.alignment.center
        )
    
    def crear_vista_tablero_juego(self, estado_juego, nombre_usuario, al_click_celda, al_presion_larga_celda, al_usuario, al_estadisticas, al_nuevo_juego, al_salir):
        """Crea la vista del tablero de juego"""
        tablero = self._crear_tablero_ui(
            estado_juego["tablero"],
            al_click_celda,
            al_presion_larga_celda
        )
        
        # Barra de información superior
        info_superior = ft.Row([
            self.contador_minas,
            self.dificultad_actual,
            ft.Text(f"Jugador: {nombre_usuario}", size=14),
        ], alignment="spaceBetween")
        
        return ft.Container(
            content=ft.Column([
                # Encabezado con pestañas
                ft.Text("Buscaminas", size=24, weight="bold"),
                ft.Row([
                    ft.TextButton("Juego", on_click=lambda e: None),
                    ft.TextButton("Estadísticas", on_click=al_estadisticas),
                ]),
                ft.Divider(),
                
                # Información del juego
                info_superior,
                ft.Container(height=10),
                self.mensaje_estado,
                ft.Container(height=20),
                
                # Tablero
                ft.Container(
                    content=tablero,
                    alignment=ft.alignment.center
                ),
                
                ft.Container(height=20),
                
                # Botones de acción
                ft.Row([
                    ft.ElevatedButton("Nuevo Juego", on_click=al_nuevo_juego),
                    ft.ElevatedButton("Salir del Juego", on_click=al_salir),
                ], alignment="center", spacing=20)
                
            ]),
            padding=20
        )
    
    def _crear_tablero_ui(self, tablero, al_click_celda, al_presion_larga_celda):
        """Crea la interfaz gráfica del tablero"""
        grid = ft.GridView(
            expand=False,
            max_extent=35,
            child_aspect_ratio=1.0,
            spacing=1,
            run_spacing=1,
        )
        
        for fila_idx, fila in enumerate(tablero):
            for col_idx, celda in enumerate(fila):
                boton_celda = self._crear_boton_celda(
                    celda, 
                    fila_idx, 
                    col_idx, 
                    al_click_celda, 
                    al_presion_larga_celda
                )
                grid.controls.append(boton_celda)
        
        return grid
    
    def _crear_boton_celda(self, celda, fila, columna, al_click, al_presion_larga):
        """Crea un botón para una celda del tablero"""
        contenido = self._obtener_contenido_celda(celda)
        color_fondo, color_borde = self._obtener_estilo_celda(celda)
        
        boton = ft.Container(
            content=contenido,
            width=35,
            height=35,
            bgcolor=color_fondo,
            border=ft.border.all(1, color_borde),
            border_radius=2,
            alignment=ft.alignment.center,
            on_click=lambda e, f=fila, c=columna: al_click(f, c),
            on_long_press=lambda e, f=fila, c=columna: al_presion_larga(f, c),
        )
        
        return boton
    
    def _obtener_contenido_celda(self, celda):
        """Obtiene el contenido visual para una celda"""
        if celda["revelada"]:
            if celda["es_mina"]:
                return ft.Text("💣", size=16)
            elif celda["minas_adyacentes"] > 0:
                color = self._obtener_color_numero(celda["minas_adyacentes"])
                return ft.Text(str(celda["minas_adyacentes"]), size=14, weight="bold", color=color)
            else:
                return ft.Text("", size=12)
        elif celda["bandera"]:
            return ft.Text("🚩", size=16)
        else:
            return ft.Text("", size=12)
    
    def _obtener_estilo_celda(self, celda):
        """Obtiene el color de fondo y borde para una celda"""
        if celda["revelada"]:
            if celda["es_mina"]:
                return "red", "darkred"
            else:
                return "lightblue", "blue"
        else:
            return "gray300", "gray"
    
    def _obtener_color_numero(self, numero):
        """Obtiene el color para los números de minas adyacentes"""
        colores = {
            1: "blue",
            2: "green", 
            3: "red",
            4: "purple",
            5: "maroon",
            6: "turquoise",
            7: "black",
            8: "gray"
        }
        return colores.get(numero, "black")
    
    def actualizar_mensaje_estado(self, mensaje: str, color: str = "blue"):
        """Actualiza el mensaje de estado"""
        self.mensaje_estado.value = mensaje
        self.mensaje_estado.color = color
    
    def actualizar_contador_minas(self, minas_restantes: int):
        """Actualiza el contador de minas"""
        self.contador_minas.value = f"Minas: {minas_restantes}"
    
    def actualizar_dificultad(self, dificultad: str):
        """Actualiza la dificultad mostrada"""
        self.dificultad_actual.value = f"Dificultad: {dificultad}"