# main.py
import flet as ft
import time
from modelos.basedatos_json import BaseDatosJSON, UsuarioDAO, PartidaDAO
from controladores.controlador_usuario import ControladorUsuario
from controladores.controlador_juego import ControladorJuego
from vistas.vista_juego import VistaJuego
from vistas.vista_estadisticas import VistaEstadisticas
from vistas.vista_inicio_sesion import VistaInicioSesion

class AplicacionBuscaminas:
    def __init__(self):
        # Inicializar base de datos JSON
        self.base_datos_json = BaseDatosJSON()
        self.dao_usuario = UsuarioDAO(self.base_datos_json)
        self.dao_partida = PartidaDAO(self.base_datos_json)
        
        # Inicializar controladores
        self.controlador_usuario = ControladorUsuario(self.dao_usuario)
        self.controlador_juego = ControladorJuego(self.dao_partida)
        
        # Inicializar vistas
        self.vista_juego = VistaJuego()
        self.vista_estadisticas = VistaEstadisticas()
        self.vista_inicio_sesion = VistaInicioSesion()
        
        # Estados
        self.pagina_actual = "inicio_sesion"
        self.pestanas = None
        self.contenido_principal = None
        self.pagina = None

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
            self.vista_juego.titulo,
            ft.Divider(),
            self.pestanas
        ])

    def crear_contenido_juego(self):
        """Crea el contenido de la pestaña de juego"""
        if not self.controlador_juego.juego_actual:
            return self.vista_juego.crear_vista_seleccion_dificultad(
                al_facil=lambda e: self.iniciar_juego("Fácil", 8, 8, 10),
                al_medio=lambda e: self.iniciar_juego("Medio", 12, 12, 30),
                al_dificil=lambda e: self.iniciar_juego("Difícil", 16, 16, 60),
                al_usuario=lambda e: self.mostrar_pagina_inicio_sesion(),
                al_estadisticas=lambda e: self.mostrar_pestana_estadisticas(),
                al_nuevo_juego=lambda e: self.mostrar_seleccion_dificultad(),
                al_salir=lambda e: self.salir_aplicacion(e)
            )
        else:
            nombre_usuario = self.controlador_usuario.obtener_estado().get('nombre_usuario', 'Invitado')
            estado_juego = self.controlador_juego.obtener_estado()
            
            # Actualizar dificultad en la vista
            self.vista_juego.actualizar_dificultad(self.controlador_juego.obtener_dificultad())
            
            return self.vista_juego.crear_vista_tablero_juego(
                estado_juego=estado_juego,
                nombre_usuario=nombre_usuario,
                al_click_celda=self.manejar_click_celda,
                al_presion_larga_celda=self.manejar_presion_larga_celda,
                al_usuario=lambda e: self.mostrar_pagina_inicio_sesion(),
                al_estadisticas=lambda e: self.mostrar_pestana_estadisticas(),
                al_nuevo_juego=lambda e: self.mostrar_seleccion_dificultad(),
                al_salir=lambda e: self.salir_aplicacion(e)
            )

    def crear_contenido_estadisticas(self):
        """Crea el contenido de la pestaña de estadísticas"""
        estadisticas = self.controlador_usuario.obtener_estado()
        
        return self.vista_estadisticas.crear_vista_estadisticas(
            estadisticas=estadisticas,
            al_actualizar=lambda e: self.actualizar_pestana_estadisticas(),
            al_inicio_sesion=lambda e: self.mostrar_pagina_inicio_sesion()
        )

    def mostrar_pagina_inicio_sesion(self, e=None):
        """Muestra la página de inicio de sesión/registro"""
        self.pagina_actual = "inicio_sesion"
        
        vista_inicio_sesion = self.vista_inicio_sesion.crear_vista_inicio_sesion(
            al_iniciar_sesion=self.manejar_inicio_sesion,
            al_registrar=self.manejar_registro
        )
        
        self.pagina.clean()
        self.pagina.add(vista_inicio_sesion)

    def mostrar_seleccion_dificultad(self, e=None):
        """Muestra la selección de dificultad"""
        self.pagina_actual = "dificultad"
        
        # Crear interfaz principal si no existe
        if not self.contenido_principal:
            self.crear_interfaz_principal()
        
        # Resetear el juego
        self.controlador_juego._juego_actual = None
        self.vista_juego.actualizar_mensaje_estado("Selecciona una dificultad para comenzar", "blue")
        
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
        usuario, _ = self.vista_inicio_sesion.obtener_datos_formulario()
        
        if not usuario:
            self.vista_inicio_sesion.mostrar_mensaje("El nombre de usuario es requerido", False)
            self.pagina.update()
            return
        
        exito, mensaje = self.controlador_usuario.iniciar_sesion(usuario)
        
        self.vista_inicio_sesion.mostrar_mensaje(mensaje, exito)
        
        if exito:
            # Limpiar formulario y mostrar selección de dificultad
            self.vista_inicio_sesion.limpiar_formulario()
            self.mostrar_seleccion_dificultad()
        
        self.pagina.update()

    def manejar_registro(self, e):
        """Maneja el intento de registro"""
        usuario, correo = self.vista_inicio_sesion.obtener_datos_formulario()
        
        if not usuario:
            self.vista_inicio_sesion.mostrar_mensaje("El nombre de usuario es requerido", False)
            self.pagina.update()
            return
        
        exito, mensaje = self.controlador_usuario.registrar(usuario, correo if correo else None)
        
        self.vista_inicio_sesion.mostrar_mensaje(mensaje, exito)
        
        if exito:
            # Limpiar formulario y mostrar selección de dificultad
            self.vista_inicio_sesion.limpiar_formulario()
            self.mostrar_seleccion_dificultad()
        
        self.pagina.update()

    def iniciar_juego(self, dificultad: str, filas: int, columnas: int, minas: int):
        """Inicia un nuevo juego con la dificultad especificada"""
        try:
            id_usuario = self.controlador_usuario.usuario_actual.id if self.controlador_usuario.usuario_actual else None
            self.controlador_juego.iniciar_nueva_partida(filas, columnas, minas, dificultad, id_usuario)
            
            # Actualizar mensaje de estado
            self.vista_juego.actualizar_mensaje_estado("¡Juego comenzado! Haz click en una celda para empezar.", "blue")
            self.vista_juego.actualizar_dificultad(dificultad)
            
            self.actualizar_contenido_juego()
        except Exception as e:
            self.vista_juego.actualizar_mensaje_estado(f"Error al iniciar juego: {str(e)}", "red")
            self.pagina.update()

    def manejar_click_celda(self, fila: int, columna: int):
        """Maneja el click en una celda"""
        try:
            exito, juego_terminado = self.controlador_juego.revelar_celda(fila, columna)
            
            if juego_terminado:
                if self.controlador_juego.juego_actual.partida_ganada:
                    self.vista_juego.actualizar_mensaje_estado("¡Felicidades! Has ganado el juego.", "green")
                    
                    # Actualizar estadísticas del usuario
                    if self.controlador_usuario.usuario_actual and self.controlador_juego.tiempo_inicio_juego:
                        duracion = int(time.time() - self.controlador_juego.tiempo_inicio_juego)
                        self.controlador_usuario.actualizar_estadisticas_usuario(
                            True, duracion, self.controlador_juego.obtener_dificultad()
                        )
                else:
                    self.vista_juego.actualizar_mensaje_estado("¡Game Over! Has pisado una mina.", "red")
                    
                    # Actualizar estadísticas del usuario
                    if self.controlador_usuario.usuario_actual and self.controlador_juego.tiempo_inicio_juego:
                        duracion = int(time.time() - self.controlador_juego.tiempo_inicio_juego)
                        self.controlador_usuario.actualizar_estadisticas_usuario(
                            False, duracion, self.controlador_juego.obtener_dificultad()
                        )
            
            # Actualizar contador de minas y grid
            if self.controlador_juego.juego_actual:
                minas_restantes = self.controlador_juego.obtener_minas_restantes()
                self.vista_juego.actualizar_contador_minas(minas_restantes)
            
            self.actualizar_contenido_juego()
            
        except Exception as e:
            self.vista_juego.actualizar_mensaje_estado(f"Error: {str(e)}", "red")
            self.pagina.update()

    def manejar_presion_larga_celda(self, fila: int, columna: int):
        """Maneja el click largo (bandera) en una celda"""
        try:
            self.controlador_juego.alternar_bandera(fila, columna)
            if self.controlador_juego.juego_actual:
                minas_restantes = self.controlador_juego.obtener_minas_restantes()
                self.vista_juego.actualizar_contador_minas(minas_restantes)
            self.actualizar_contenido_juego()
        except Exception as e:
            self.vista_juego.actualizar_mensaje_estado(f"Error: {str(e)}", "red")
            self.pagina.update()

    def salir_aplicacion(self, e):
        """Cierra la aplicación"""
        self.vista_juego.actualizar_mensaje_estado("Para salir, cierre la ventana del navegador", "orange")
        self.pagina.update()

def main(pagina: ft.Page):
    aplicacion = AplicacionBuscaminas()
    aplicacion.construir(pagina)

if __name__ == "__main__":
    ft.app(target=main)