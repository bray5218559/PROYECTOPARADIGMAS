# main.py
import flet as ft
import time
from modelos.basedatos_json import BaseDatosJSON, UsuarioDAO, PartidaDAO
from controladores.controlador_usuario import ControladorUsuario
from controladores.controlador_juego import ControladorJuego

class AplicacionBuscaminas:
    def __init__(self):
        # Inicializar base de datos JSON
        self.base_datos_json = BaseDatosJSON()
        self.dao_usuario = UsuarioDAO(self.base_datos_json)
        self.dao_partida = PartidaDAO(self.base_datos_json)
        
        # Inicializar controladores
        self.controlador_usuario = ControladorUsuario(self.dao_usuario)
        self.controlador_juego = ControladorJuego(self.dao_partida)
        
        # Elementos de UI
        self.titulo = ft.Text("BUSCAMINAS", size=32, weight="bold", color="blue900")
        self.texto_dificultad = ft.Text("Dificultad: Fácil", size=16, weight="bold")
        self.contador_minas = ft.Text("Minas: 0", size=16, weight="bold")
        self.mensaje_estado = ft.Text("¡Bienvenido! Selecciona una dificultad para comenzar.", 
                                    size=16, weight="bold", color="blue")
        
        # Estados
        self.pagina_actual = "inicio_sesion"
        self.pestanas = None
        self.contenido_principal = None

    def construir(self, pagina: ft.Page):
        self.pagina = pagina
        pagina.title = "Buscaminas"
        pagina.horizontal_alignment = "center"
        pagina.vertical_alignment = "center"
        pagina.theme_mode = "light"
        pagina.padding = 20
        
        # Mostrar página de inicio de sesión inicialmente
        self.mostrar_pagina_inicio_sesion()

    def crear_interfaz_principal(self):
        """Crea la interfaz principal con pestañas"""
        # Crear las pestañas
        self.pestanas = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Juego",
                    content=ft.Container(content=self.crear_contenido_juego())
                ),
                ft.Tab(
                    text="Estadísticas",
                    content=self.crear_contenido_estadisticas()
                ),
            ],
            on_change=self.cambio_pestana
        )
        
        # Layout principal
        self.contenido_principal = ft.Column([
            self.titulo,
            ft.Divider(),
            self.pestanas
        ])

    def crear_contenido_juego(self):
        """Crea el contenido de la pestaña de juego"""
        if not self.controlador_juego.juego_actual:
            return self.crear_seleccion_dificultad()
        else:
            return self.crear_tablero_juego()

    def crear_seleccion_dificultad(self):
        """Crea la interfaz de selección de dificultad"""
        return ft.Column([
            ft.Text("Selección de Dificultad", size=20, weight="bold"),
            self.crear_botones_dificultad(),
            ft.Divider(),
            self.texto_dificultad,
            self.contador_minas,
            self.mensaje_estado,
            ft.Container(content=ft.Text("Selecciona una dificultad para comenzar", size=16, color="gray")),
            self.crear_botones_accion(),
            self.crear_instrucciones()
        ], alignment="center", horizontal_alignment="center", spacing=15)

    def crear_tablero_juego(self):
        """Crea el tablero de juego actual"""
        estado_juego = self.controlador_juego.obtener_estado()
        
        # Actualizar elementos de UI
        self.texto_dificultad.value = f"Dificultad: {self.controlador_juego.obtener_dificultad()}"
        self.contador_minas.value = f"Minas: {self.controlador_juego.obtener_minas_restantes()}"
        
        # Crear grid de juego
        grid_juego = self.crear_grid_juego(estado_juego)
        
        info_usuario = ft.Row([
            ft.Icon(ft.Icons.PERSON, color="blue"),
            ft.Text(f"Jugando como: {self.controlador_usuario.obtener_estado().get('nombre_usuario', 'Invitado')}", 
                   size=14),
        ], alignment="center")
        
        return ft.Column([
            info_usuario,
            ft.Row([self.texto_dificultad, self.contador_minas], alignment="center"),
            self.mensaje_estado,
            ft.Container(content=grid_juego, padding=10),
            self.crear_botones_accion()
        ], alignment="center", horizontal_alignment="center", spacing=15)

    def crear_grid_juego(self, estado_juego: dict):
        """Crea el grid de juego basado en el estado actual"""
        filas = estado_juego['filas']
        columnas = estado_juego['columnas']
        
        # Crear un grid de contenedores
        controles_grid = []
        for fila in range(filas):
            controles_fila = []
            for columna in range(columnas):
                celda = self.crear_celda(fila, columna, estado_juego)
                controles_fila.append(celda)
            
            # Crear una fila con las celdas
            fila_grid = ft.Row(controls=controles_fila, alignment="center")
            controles_grid.append(fila_grid)
        
        # Crear el grid como una columna de filas
        return ft.Column(controls=controles_grid, spacing=2)

    def crear_celda(self, fila: int, columna: int, estado_juego: dict):
        """Crea una celda individual basada en su estado"""
        celda = ft.Container(
            width=35,
            height=35,
            alignment=ft.alignment.center,
            border_radius=3,
            on_click=lambda e: self.manejar_click_celda(fila, columna),
            on_long_press=lambda e: self.manejar_presion_larga_celda(fila, columna),
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

    def crear_botones_dificultad(self):
        """Crea los botones de selección de dificultad"""
        return ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Fácil (8x8 - 10 minas)", 
                    on_click=lambda e: self.iniciar_juego("Fácil", 8, 8, 10), 
                    bgcolor="green400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Medio (12x12 - 30 minas)", 
                    on_click=lambda e: self.iniciar_juego("Medio", 12, 12, 30), 
                    bgcolor="orange400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Difícil (16x16 - 60 minas)", 
                    on_click=lambda e: self.iniciar_juego("Difícil", 16, 16, 60), 
                    bgcolor="red400", 
                    color="white"
                ),
            ],
            alignment="center",
            spacing=10,
        )

    def crear_botones_accion(self):
        """Crea los botones de acción principales"""
        return ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Usuario", 
                    icon="person", 
                    on_click=lambda e: self.mostrar_pagina_inicio_sesion(),
                    bgcolor="blue400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Estadísticas", 
                    icon="leaderboard", 
                    on_click=lambda e: self.mostrar_pestana_estadisticas(),
                    bgcolor="green400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Nuevo Juego", 
                    icon="replay", 
                    on_click=lambda e: self.mostrar_seleccion_dificultad(),
                    bgcolor="blue400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Salir", 
                    icon="exit_to_app", 
                    on_click=lambda e: self.salir_aplicacion(e),
                    bgcolor="red400", 
                    color="white"
                ),
            ],
            alignment="center",
            spacing=10,
        )

    def crear_instrucciones(self):
        """Crea el panel de instrucciones"""
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

    def crear_contenido_estadisticas(self):
        """Crea el contenido de la pestaña de estadísticas"""
        if not self.controlador_usuario.usuario_actual:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.WARNING, size=48, color="orange"),
                    ft.Text("Debes iniciar sesión", size=18, weight="bold"),
                    ft.Text("Inicia sesión para ver tus estadísticas", size=14, color="gray"),
                    ft.ElevatedButton(
                        "Ir a Inicio de Sesión",
                        icon=ft.Icons.LOGIN,
                        on_click=lambda e: self.mostrar_pagina_inicio_sesion(),
                        bgcolor="blue400",
                        color="white"
                    )
                ], alignment="center", horizontal_alignment="center", spacing=15),
                padding=20
            )
        else:
            return self.crear_interfaz_estadisticas()

    def crear_interfaz_estadisticas(self):
        """Crea la interfaz de estadísticas con los datos del usuario"""
        estadisticas = self.controlador_usuario.obtener_estado()
        
        if not estadisticas or not estadisticas.get('nombre_usuario'):
            return ft.Column([
                ft.Icon(ft.Icons.INFO, size=48, color="blue"),
                ft.Text("No hay datos disponibles", size=18, weight="bold"),
                ft.Text("Juega algunas partidas para generar estadísticas", size=14, color="gray")
            ], alignment="center", horizontal_alignment="center", spacing=15)
        
        # Tarjeta de resumen general
        tarjeta_resumen = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Resumen General", size=20, weight="bold", color="blue"),
                    ft.Divider(),
                    ft.Row([
                        self.crear_elemento_estadistica("Partidas Totales", estadisticas['partidas_totales'], ft.Icons.SPORTS_ESPORTS),
                        self.crear_elemento_estadistica("Partidas Ganadas", estadisticas['partidas_ganadas'], ft.Icons.EMOJI_EVENTS),
                        self.crear_elemento_estadistica("Partidas Perdidas", estadisticas['partidas_perdidas'], ft.Icons.MOOD_BAD),
                    ], alignment="space_around"),
                    ft.Container(
                        content=ft.Row([
                            self.crear_elemento_estadistica("Porcentaje de Victoria", 
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
        
        # Tarjeta de mejores tiempos
        tarjeta_tiempos = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Mejores Tiempos", size=20, weight="bold", color="green"),
                    ft.Divider(),
                    ft.Row([
                        self.crear_elemento_tiempo("Fácil", estadisticas.get('mejor_tiempo_facil'), "🟢"),
                        self.crear_elemento_tiempo("Medio", estadisticas.get('mejor_tiempo_medio'), "🟡"),
                        self.crear_elemento_tiempo("Difícil", estadisticas.get('mejor_tiempo_dificil'), "🔴"),
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
                ft.Text(f"Estadísticas de {estadisticas['nombre_usuario']}", 
                       size=22, weight="bold", color="blue")
            ], alignment="center"),
            tarjeta_resumen,
            tarjeta_tiempos,
            ft.ElevatedButton(
                "Actualizar Estadísticas",
                icon=ft.Icons.REFRESH,
                on_click=lambda e: self.actualizar_pestana_estadisticas(),
                bgcolor="blue400",
                color="white"
            )
        ], spacing=20)

    def crear_elemento_estadistica(self, etiqueta: str, valor, icono):
        """Crea un elemento de estadística individual"""
        return ft.Column([
            ft.Icon(icono, size=30, color="blue"),
            ft.Text(str(valor), size=24, weight="bold"),
            ft.Text(etiqueta, size=12, color="gray", text_align="center")
        ], horizontal_alignment="center", spacing=5)

    def crear_elemento_tiempo(self, dificultad: str, valor_tiempo, emoji: str):
        """Crea un elemento de tiempo individual"""
        tiempo_mostrar = f"{valor_tiempo}s" if valor_tiempo else "No registrado"
        color = "green" if dificultad == "Fácil" else "orange" if dificultad == "Medio" else "red"
        
        return ft.Column([
            ft.Text(emoji, size=30),
            ft.Text(dificultad, size=14, weight="bold", color=color),
            ft.Text(tiempo_mostrar, size=16, weight="bold"),
            ft.Text("mejor tiempo", size=10, color="gray")
        ], horizontal_alignment="center", spacing=5)

    def mostrar_pagina_inicio_sesion(self, e=None):
        """Muestra la página de inicio de sesión/registro"""
        self.pagina_actual = "inicio_sesion"
        
        # Crear formulario de inicio de sesión/registro
        self.campo_nombre_usuario = ft.TextField(
            label="Nombre de usuario", 
            width=300,
            autofocus=True,
            hint_text="Ejemplo: maria"
        )
        self.campo_correo = ft.TextField(
            label="Email (opcional)", 
            width=300,
            hint_text="Ejemplo: maria@email.com"
        )
        self.texto_mensaje = ft.Text("", color="red", size=12)
        
        formulario_inicio_sesion = ft.Column([
            self.titulo,
            ft.Text("Bienvenido al Buscaminas", size=20, weight="bold"),
            ft.Text("Por favor, inicia sesión o regístrate para continuar", size=16),
            ft.Divider(),
            
            ft.Text("Nombre de usuario:", weight="bold"),
            self.campo_nombre_usuario,
            
            ft.Text("Email (opcional):", weight="bold"),
            self.campo_correo,
            
            self.texto_mensaje,
            
            ft.Row([
                ft.ElevatedButton(
                    "Iniciar Sesión",
                    icon=ft.Icons.LOGIN,
                    on_click=self.manejar_inicio_sesion,
                    bgcolor="blue400",
                    color="white",
                    width=150
                ),
                ft.ElevatedButton(
                    "Registrarse",
                    icon=ft.Icons.PERSON_ADD,
                    on_click=self.manejar_registro,
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
        
        self.pagina.clean()
        self.pagina.add(formulario_inicio_sesion)

    def mostrar_seleccion_dificultad(self, e=None):
        """Muestra la selección de dificultad"""
        self.pagina_actual = "dificultad"
        
        # Crear interfaz principal si no existe
        if not self.contenido_principal:
            self.crear_interfaz_principal()
        
        # Resetear el juego
        self.controlador_juego._juego_actual = None
        self.mensaje_estado.value = "Selecciona una dificultad para comenzar"
        self.mensaje_estado.color = "blue"
        
        self.pagina.clean()
        self.pagina.add(self.contenido_principal)
        self.pestanas.selected_index = 0
        self.actualizar_contenido_juego()

    def mostrar_pestana_estadisticas(self, e=None):
        """Muestra la pestaña de estadísticas"""
        if not self.contenido_principal:
            self.crear_interfaz_principal()
        
        self.pestanas.selected_index = 1
        self.actualizar_pestana_estadisticas()
        self.pagina.update()

    def cambio_pestana(self, e):
        """Maneja el cambio de pestañas"""
        if self.pestanas.selected_index == 0:  # Pestaña de Juego
            self.actualizar_contenido_juego()
        elif self.pestanas.selected_index == 1:  # Pestaña de Estadísticas
            self.actualizar_pestana_estadisticas()

    def actualizar_contenido_juego(self):
        """Actualiza el contenido de la pestaña de juego"""
        contenido_juego = self.crear_contenido_juego()
        pestana_juego = self.pestanas.tabs[0]
        pestana_juego.content = contenido_juego
        self.pagina.update()

    def actualizar_pestana_estadisticas(self):
        """Actualiza el contenido de la pestaña de estadísticas"""
        contenido_estadisticas = self.crear_contenido_estadisticas()
        pestana_estadisticas = self.pestanas.tabs[1]
        pestana_estadisticas.content = contenido_estadisticas
        self.pagina.update()

    def manejar_inicio_sesion(self, e):
        """Maneja el intento de inicio de sesión"""
        nombre_usuario = self.campo_nombre_usuario.value.strip()
        if not nombre_usuario:
            self.texto_mensaje.value = "El nombre de usuario es requerido"
            self.texto_mensaje.color = "red"
            self.pagina.update()
            return
        
        exito, mensaje = self.controlador_usuario.iniciar_sesion(nombre_usuario)
        
        self.texto_mensaje.value = mensaje
        self.texto_mensaje.color = "green" if exito else "red"
        
        if exito:
            # Limpiar campos
            self.campo_nombre_usuario.value = ""
            self.campo_correo.value = ""
            self.mostrar_seleccion_dificultad()
        
        self.pagina.update()

    def manejar_registro(self, e):
        """Maneja el intento de registro"""
        nombre_usuario = self.campo_nombre_usuario.value.strip()
        correo = self.campo_correo.value.strip()
        
        if not nombre_usuario:
            self.texto_mensaje.value = "El nombre de usuario es requerido"
            self.texto_mensaje.color = "red"
            self.pagina.update()
            return
        
        exito, mensaje = self.controlador_usuario.registrar(nombre_usuario, correo if correo else None)
        
        self.texto_mensaje.value = mensaje
        self.texto_mensaje.color = "green" if exito else "red"
        
        if exito:
            # Limpiar campos
            self.campo_nombre_usuario.value = ""
            self.campo_correo.value = ""
            self.mostrar_seleccion_dificultad()
        
        self.pagina.update()

    def iniciar_juego(self, dificultad: str, filas: int, columnas: int, minas: int):
        """Inicia un nuevo juego con la dificultad especificada"""
        id_usuario = self.controlador_usuario.usuario_actual.id if self.controlador_usuario.usuario_actual else None
        self.controlador_juego.iniciar_nueva_partida(filas, columnas, minas, dificultad, id_usuario)
        
        # Actualizar mensaje de estado
        self.mensaje_estado.value = "¡Juego comenzado! Haz click en una celda para empezar."
        self.mensaje_estado.color = "blue"
        
        self.actualizar_contenido_juego()

    def manejar_click_celda(self, fila: int, columna: int):
        """Maneja el click en una celda"""
        exito, juego_terminado = self.controlador_juego.revelar_celda(fila, columna)
        
        if juego_terminado:
            if self.controlador_juego.juego_actual.partida_ganada:
                self.mensaje_estado.value = "¡Felicidades! Has ganado el juego."
                self.mensaje_estado.color = "green"
                
                # Actualizar estadísticas del usuario
                if self.controlador_usuario.usuario_actual and self.controlador_juego.tiempo_inicio_juego:
                    duracion = int(time.time() - self.controlador_juego.tiempo_inicio_juego)
                    self.controlador_usuario.actualizar_estadisticas_usuario(
                        True, duracion, self.controlador_juego.obtener_dificultad()
                    )
            else:
                self.mensaje_estado.value = "¡Game Over! Has pisado una mina."
                self.mensaje_estado.color = "red"
                
                # Actualizar estadísticas del usuario
                if self.controlador_usuario.usuario_actual and self.controlador_juego.tiempo_inicio_juego:
                    duracion = int(time.time() - self.controlador_juego.tiempo_inicio_juego)
                    self.controlador_usuario.actualizar_estadisticas_usuario(
                        False, duracion, self.controlador_juego.obtener_dificultad()
                    )
        
        # Actualizar contador de minas y grid
        if self.controlador_juego.juego_actual:
            self.contador_minas.value = f"Minas: {self.controlador_juego.obtener_minas_restantes()}"
        self.actualizar_contenido_juego()

    def manejar_presion_larga_celda(self, fila: int, columna: int):
        """Maneja el click largo (bandera) en una celda"""
        self.controlador_juego.alternar_bandera(fila, columna)
        if self.controlador_juego.juego_actual:
            self.contador_minas.value = f"Minas: {self.controlador_juego.obtener_minas_restantes()}"
        self.actualizar_contenido_juego()

    def salir_aplicacion(self, e):
        """Cierra la aplicación"""
        self.mensaje_estado.value = "Para salir, cierre la ventana del navegador"
        self.mensaje_estado.color = "orange"
        self.pagina.update()

def main(pagina: ft.Page):
    aplicacion = AplicacionBuscaminas()
    aplicacion.construir(pagina)

if __name__ == "__main__":
    ft.app(target=main)