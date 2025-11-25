# vistas/vista_inicio_sesion.py
import flet as ft
from typing import Callable
from vistas.componentes_ui import FabricaComponentesUI

class VistaInicioSesion:
    """Vista responsable de mostrar la interfaz de inicio de sesión y registro"""
    
    def __init__(self):
        self.fabrica = FabricaComponentesUI()
        self.titulo = self.fabrica.crear_titulo()
        self.campo_usuario = None
        self.campo_correo = None
        self.texto_mensaje = None

    def crear_vista_inicio_sesion(self, 
                                al_iniciar_sesion: Callable, 
                                al_registrar: Callable) -> ft.Column:
        """Crea la vista de inicio de sesión/registro"""
        
        self.campo_usuario = ft.TextField(
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
        
        return ft.Column([
            self.titulo,
            ft.Text("Bienvenido al Buscaminas", size=20, weight="bold"),
            ft.Text("Por favor, inicia sesión o regístrate para continuar", size=16),
            ft.Divider(),
            
            ft.Text("Nombre de usuario:", weight="bold"),
            self.campo_usuario,
            
            ft.Text("Email (opcional):", weight="bold"),
            self.campo_correo,
            
            self.texto_mensaje,
            
            ft.Row([
                ft.ElevatedButton(
                    "Iniciar Sesión",
                    icon=ft.Icons.LOGIN,
                    on_click=al_iniciar_sesion,
                    bgcolor="blue400",
                    color="white",
                    width=150
                ),
                ft.ElevatedButton(
                    "Registrarse",
                    icon=ft.Icons.PERSON_ADD,
                    on_click=al_registrar,
                    bgcolor="green400",
                    color="white",
                    width=150
                )
            ], alignment="center", spacing=20),
            
            self._crear_panel_ayuda()
        ], alignment="center", horizontal_alignment="center", spacing=15)

    def _crear_panel_ayuda(self) -> ft.Container:
        """Crea el panel de ayuda para usuarios nuevos"""
        return ft.Container(
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

    def obtener_datos_formulario(self) -> tuple[str, str]:
        """Obtiene los datos del formulario"""
        usuario = self.campo_usuario.value.strip() if self.campo_usuario else ""
        correo = self.campo_correo.value.strip() if self.campo_correo else ""
        return usuario, correo

    def limpiar_formulario(self):
        """Limpia los campos del formulario"""
        if self.campo_usuario:
            self.campo_usuario.value = ""
        if self.campo_correo:
            self.campo_correo.value = ""

    def mostrar_mensaje(self, mensaje: str, es_exito: bool = False):
        """Muestra un mensaje al usuario"""
        if self.texto_mensaje:
            self.texto_mensaje.value = mensaje
            self.texto_mensaje.color = "green" if es_exito else "red"