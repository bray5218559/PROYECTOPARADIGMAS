# main.py (versión actualizada)
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

    # ... (el resto de métodos del main se mantienen igual, pero usando las vistas)
    # Los métodos como mostrar_pagina_inicio_sesion, manejar_inicio_sesion, etc.
    # se actualizan para usar las nuevas vistas

def main(pagina: ft.Page):
    aplicacion = AplicacionBuscaminas()
    aplicacion.construir(pagina)

if __name__ == "__main__":
    ft.app(target=main)