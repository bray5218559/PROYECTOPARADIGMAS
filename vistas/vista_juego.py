# vistas/vista_juego.py
import flet as ft

class VistaJuego:
    def __init__(self):
        # Elementos de UI principales
        self.titulo = ft.Text("BUSCAMINAS", size=24, weight="bold", text_align="center")
        self.texto_dificultad = ft.Text("Dificultad: No seleccionada", size=16, weight="bold")
        self.contador_minas = ft.Text("Minas: 0", size=16, weight="bold")
        self.mensaje_estado = ft.Text("Selecciona una dificultad para comenzar", size=14, color="blue")
        
    def crear_vista_seleccion_dificultad(self, al_facil, al_medio, al_dificil, al_usuario, al_estadisticas, al_nuevo_juego, al_salir):
        """Crea la vista de selección de dificultad"""
        
        # Botones de dificultad
        botones_dificultad = ft.Row([
            ft.ElevatedButton(
                "Fácil (8x8 - 10 minas)",
                icon="star_outline",
                on_click=al_facil,
                bgcolor="green400",
                color="white",
                width=200
            ),
            ft.ElevatedButton(
                "Medio (12x12 - 30 minas)",
                icon="star_half",
                on_click=al_medio,
                bgcolor="orange400",
                color="white",
                width=200
            ),
            ft.ElevatedButton(
                "Difícil (16x16 - 60 minas)",
                icon="star",
                on_click=al_dificil,
                bgcolor="red400",
                color="white",
                width=200
            )
        ], alignment="center", spacing=20)
        
        # Botones de acción
        botones_accion = self.crear_botones_accion(al_usuario, al_estadisticas, al_nuevo_juego, al_salir)
        
        # Instrucciones
        instrucciones = self.crear_instrucciones()
        
        contenido = ft.Column([
            ft.Text("Selecciona la dificultad:", size=20, weight="bold"),
            botones_dificultad,
            ft.Divider(),
            botones_accion,
            instrucciones
        ], alignment="center", horizontal_alignment="center", spacing=20)
        
        return contenido

    def crear_vista_tablero_juego(self, estado_juego, nombre_usuario, al_click_celda, al_presion_larga_celda, 
                                 al_usuario, al_estadisticas, al_nuevo_juego, al_salir):
        """Crea la vista completa del tablero de juego"""
        
        # Actualizar elementos de UI
        self.actualizar_dificultad(estado_juego.get('dificultad', 'Desconocida'))
        self.actualizar_contador_minas(estado_juego.get('minas_restantes', 0))
        
        # Crear grid de juego
        grid_juego = self.crear_grid_juego(estado_juego, al_click_celda, al_presion_larga_celda)
        
        # Botones de acción
        botones_accion = self.crear_botones_accion(
            al_usuario, al_estadisticas, al_nuevo_juego, al_salir
        )
        
        # Información del usuario
        info_usuario = ft.Row([
            ft.Icon(name="person", color="blue"),
            ft.Text(f"Jugando como: {nombre_usuario}", size=14),
        ], alignment="center")
        
        # Layout completo
        contenido = ft.Column([
            info_usuario,
            ft.Row([self.texto_dificultad, self.contador_minas], alignment="center", spacing=30),
            self.mensaje_estado,
            grid_juego,
            botones_accion
        ], alignment="center", horizontal_alignment="center", spacing=15)
        
        return contenido

    def crear_grid_juego(self, estado_juego, al_click_celda, al_presion_larga_celda):
        """Crea el grid visual del buscaminas"""
        filas = estado_juego['filas']
        columnas = estado_juego['columnas']
        tablero = estado_juego['tablero']
        reveladas = estado_juego['reveladas']
        banderas = estado_juego['banderas']
        
        # Crear contenedor del grid usando Column y Row para mejor control
        filas_grid = []
        
        for fila in range(filas):
            celdas_fila = []
            for columna in range(columnas):
                celda = self.crear_celda_visual(
                    fila, columna, tablero, reveladas, banderas, 
                    al_click_celda, al_presion_larga_celda
                )
                celdas_fila.append(celda)
            
            fila_container = ft.Row(
                controls=celdas_fila,
                alignment="center",
                spacing=1
            )
            filas_grid.append(fila_container)
        
        grid_container = ft.Column(
            controls=filas_grid,
            alignment="center",
            spacing=1
        )
        
        return grid_container

    def crear_celda_visual(self, fila, columna, tablero, reveladas, banderas, al_click, al_presion_larga):
        """Crea una celda individual del buscaminas"""
        
        # Determinar el contenido y color de la celda
        if reveladas[fila][columna]:
            # Celda revelada
            bgcolor = "white"
            borde = ft.border.all(1, "grey")
            
            if tablero[fila][columna] == -1:
                # Mina
                contenido = ft.Text("💣", size=12)
                bgcolor = "red"
            elif tablero[fila][columna] > 0:
                # Número
                colores = ["blue", "green", "red", "purple", "maroon", "turquoise", "black", "gray"]
                color_texto = colores[tablero[fila][columna] - 1] if tablero[fila][columna] <= len(colores) else "black"
                contenido = ft.Text(str(tablero[fila][columna]), size=12, weight="bold", color=color_texto)
            else:
                # Celda vacía
                contenido = ft.Text("", size=12)
        elif banderas[fila][columna]:
            # Bandera
            bgcolor = "yellow"
            contenido = ft.Text("🚩", size=12)
            borde = ft.border.all(1, "darkgrey")
        else:
            # Celda no revelada
            bgcolor = "grey300"
            contenido = ft.Text("", size=12)
            borde = ft.border.all(1, "darkgrey")
        
        # Crear contenedor de la celda
        celda = ft.Container(
            width=35,
            height=35,
            alignment=ft.alignment.center,
            border_radius=3,
            bgcolor=bgcolor,
            border=borde,
            content=contenido,
            on_click=lambda e, f=fila, c=columna: al_click(f, c),
            on_long_press=lambda e, f=fila, c=columna: al_presion_larga(f, c),
        )
        
        return celda

    def crear_botones_accion(self, al_usuario, al_estadisticas, al_nuevo_juego, al_salir):
        """Crea la barra de botones de acción"""
        return ft.Row([
            ft.ElevatedButton(
                "Cambiar Usuario",
                icon="person",
                on_click=al_usuario,
                bgcolor="blue400",
                color="white"
            ),
            ft.ElevatedButton(
                "Estadísticas",
                icon="bar_chart",
                on_click=al_estadisticas,
                bgcolor="purple400",
                color="white"
            ),
            ft.ElevatedButton(
                "Nuevo Juego",
                icon="casino",
                on_click=al_nuevo_juego,
                bgcolor="green400",
                color="white"
            ),
            ft.ElevatedButton(
                "Salir",
                icon="exit_to_app",
                on_click=al_salir,
                bgcolor="red400",
                color="white"
            )
        ], alignment="center", spacing=10)

    def crear_instrucciones(self):
        """Crea el panel de instrucciones del juego"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Instrucciones:", weight="bold", size=16),
                ft.Text("• Click izquierdo: Revelar celda"),
                ft.Text("• Click largo: Colocar/Quitar bandera"),
                ft.Text("• Objetivo: Revelar todas las celdas sin minas"),
            ], spacing=5),
            padding=15,
            bgcolor="blue50",
            border_radius=10,
            margin=10
        )

    def actualizar_dificultad(self, dificultad):
        """Actualiza el texto de dificultad"""
        self.texto_dificultad.value = f"Dificultad: {dificultad}"

    def actualizar_contador_minas(self, minas_restantes):
        """Actualiza el contador de minas"""
        self.contador_minas.value = f"Minas: {minas_restantes}"

    def actualizar_mensaje_estado(self, mensaje, color="blue"):
        """Actualiza el mensaje de estado"""
        self.mensaje_estado.value = mensaje
        self.mensaje_estado.color = color