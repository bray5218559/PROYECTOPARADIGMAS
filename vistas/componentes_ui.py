# vistas/componentes_ui.py
import flet as ft
from typing import Callable, Optional, Dict, Any

class DialogoBase:
    """Clase base para diálogos"""
    def __init__(self):
        self.dialogo = None
    
    def mostrar(self, pagina: ft.Page):
        if self.dialogo:
            pagina.dialog = self.dialogo
            self.dialogo.open = True
            pagina.update()
    
    def cerrar(self, pagina: ft.Page):
        if self.dialogo:
            self.dialogo.open = False
            pagina.update()

class DialogoUsuario(DialogoBase):
    def __init__(self, al_iniciar_sesion: Callable, al_registrar: Callable, al_cerrar: Callable):
        super().__init__()
        self.campo_usuario = ft.TextField(label="Nombre de usuario", width=300)
        self.campo_correo = ft.TextField(label="Email (opcional)", width=300)
        self.texto_mensaje = ft.Text("", color="red", size=12)
        
        self.dialogo = ft.AlertDialog(
            title=ft.Text("Iniciar Sesión / Registrarse"),
            content=ft.Column([
                self.campo_usuario,
                self.campo_correo,
                self.texto_mensaje
            ], tight=True),
            actions=[
                ft.TextButton("Iniciar Sesión", on_click=al_iniciar_sesion),
                ft.TextButton("Registrarse", on_click=al_registrar),
                ft.TextButton("Cerrar", on_click=al_cerrar)
            ],
            actions_alignment="end"
        )
    
    def obtener_usuario(self) -> str:
        return self.campo_usuario.value or ""
    
    def obtener_correo(self) -> str:
        return self.campo_correo.value or ""
    
    def establecer_mensaje(self, mensaje: str, es_error: bool = True):
        self.texto_mensaje.value = mensaje
        self.texto_mensaje.color = "red" if es_error else "green"

class DialogoEstadisticas(DialogoBase):
    def __init__(self, datos_usuario: Dict[str, Any], al_cerrar: Callable):
        super().__init__()
        
        # Calcular partidas perdidas
        partidas_totales = datos_usuario.get('partidas_totales', 0)
        partidas_ganadas = datos_usuario.get('partidas_ganadas', 0)
        partidas_perdidas = partidas_totales - partidas_ganadas
        
        # Crear contenido de estadísticas
        contenido = []
        if datos_usuario and datos_usuario.get('nombre_usuario'):
            # Encabezado con nombre de usuario
            contenido.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(name="person", color="blue", size=24),
                        ft.Text(f"{datos_usuario['nombre_usuario']}", size=20, weight="bold")
                    ]),
                    padding=5,
                    margin=5
                )
            )
            
            # Estadísticas principales
            contenido.extend([
                ft.Divider(),
                ft.Text("ESTADÍSTICAS GENERALES", size=16, weight="bold", color="blue"),
                
                # Partidas totales, ganadas y perdidas
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name="sports_esports", color="blue"),
                            ft.Text(f"Partidas totales: {partidas_totales}", size=14, weight="bold")
                        ]),
                        ft.Row([
                            ft.Icon(name="emoji_events", color="green"),
                            ft.Text(f"Partidas ganadas: {partidas_ganadas}", size=14, weight="bold", color="green")
                        ]),
                        ft.Row([
                            ft.Icon(name="mood_bad", color="red"),
                            ft.Text(f"Partidas perdidas: {partidas_perdidas}", size=14, weight="bold", color="red")
                        ])
                    ], spacing=5),
                    padding=10,
                    bgcolor="grey100",
                    border_radius=10,
                    margin=5
                ),
                
                # Porcentaje de victorias
                ft.Container(
                    content=ft.Column([
                        ft.Text("EFECTIVIDAD", size=14, weight="bold"),
                        ft.Text(f"{datos_usuario.get('porcentaje_victorias', 0):.1f}% de victorias", 
                               size=16, weight="bold", 
                               color="green" if datos_usuario.get('porcentaje_victorias', 0) > 50 else "orange")
                    ], horizontal_alignment="center"),
                    padding=10,
                    bgcolor="blue50",
                    border_radius=10,
                    margin=5
                ),
                
                ft.Divider(),
                ft.Text("MEJORES TIEMPOS", size=16, weight="bold", color="blue"),
                
                # Mejores tiempos por dificultad
                ft.Container(
                    content=ft.Column([
                        self._crear_fila_tiempo("Fácil", datos_usuario.get('mejor_tiempo_facil'), "🟢"),
                        self._crear_fila_tiempo("Medio", datos_usuario.get('mejor_tiempo_medio'), "🟡"),
                        self._crear_fila_tiempo("Difícil", datos_usuario.get('mejor_tiempo_dificil'), "🔴")
                    ]),
                    padding=10,
                    bgcolor="grey50",
                    border_radius=10,
                    margin=5
                )
            ])
        else:
            contenido = [
                ft.Text("No hay datos de estadísticas disponibles", size=14),
                ft.Text("Juega algunas partidas para ver tus estadísticas", size=12, color="grey")
            ]
        
        self.dialogo = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(name="leaderboard", color="blue"),
                ft.Text("Estadísticas del Jugador")
            ]),
            content=ft.Column(contenido, scroll="adaptive"),
            actions=[ft.TextButton("Cerrar", on_click=al_cerrar)],
        )
    
    def _crear_fila_tiempo(self, dificultad: str, valor_tiempo: Any, emoji: str):
        """Crea una fila para mostrar el mejor tiempo de una dificultad"""
        texto_tiempo = f"{valor_tiempo} segundos" if valor_tiempo is not None else "No registrado"
        color = "green" if valor_tiempo is not None else "gray"
        
        return ft.Row([
            ft.Text(emoji, size=16),
            ft.Text(f"{dificultad}:", size=14, weight="bold", width=80),
            ft.Text(texto_tiempo, size=14, color=color)
        ])

class FabricaComponentesUI:
    """Fábrica para crear componentes de UI reutilizables"""
    
    @staticmethod
    def crear_titulo():
        return ft.Text("BUSCAMINAS", size=32, weight="bold", color="blue900")

    @staticmethod
    def crear_texto_dificultad():
        return ft.Text("Dificultad: Fácil", size=16, weight="bold")

    @staticmethod
    def crear_contador_minas():
        return ft.Text("Minas: 0", size=16, weight="bold")

    @staticmethod
    def crear_mensaje_estado():
        return ft.Text("¡Bienvenido! Selecciona una dificultad para comenzar.", 
                      size=16, weight="bold", color="blue")

    @staticmethod
    def crear_grid_juego(filas: int, columnas: int, al_click_celda: Callable, al_presion_larga_celda: Callable):
        return ft.GridView(
            expand=1,
            runs_count=columnas,
            max_extent=35,
            spacing=2,
            run_spacing=2,
        )

    @staticmethod
    def crear_boton_celda(fila: int, columna: int, al_click: Callable, al_presion_larga: Callable):
        return ft.Container(
            content=ft.Text("", size=12, weight="bold"),
            width=35,
            height=35,
            alignment=ft.alignment.center,
            bgcolor="grey300",
            border_radius=3,
            on_click=lambda e: al_click(fila, columna),
            on_long_press=lambda e: al_presion_larga(fila, columna),
        )

    @staticmethod
    def crear_botones_dificultad(al_facil: Callable, al_medio: Callable, al_dificil: Callable):
        return ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Fácil (8x8 - 10 minas)", 
                    on_click=al_facil, 
                    bgcolor="green400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Medio (12x12 - 30 minas)", 
                    on_click=al_medio, 
                    bgcolor="orange400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Difícil (16x16 - 60 minas)", 
                    on_click=al_dificil, 
                    bgcolor="red400", 
                    color="white"
                ),
            ],
            alignment="center",
            spacing=10,
        )

    @staticmethod
    def crear_botones_accion(al_usuario: Callable, al_estadisticas: Callable, al_nuevo_juego: Callable, al_salir: Callable):
        return ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Usuario", 
                    icon="person", 
                    on_click=al_usuario,
                    bgcolor="blue400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Estadísticas", 
                    icon="leaderboard", 
                    on_click=al_estadisticas,
                    bgcolor="green400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Nuevo Juego", 
                    icon="replay", 
                    on_click=al_nuevo_juego,
                    bgcolor="blue400", 
                    color="white"
                ),
                ft.ElevatedButton(
                    "Salir", 
                    icon="exit_to_app", 
                    on_click=al_salir,
                    bgcolor="red400", 
                    color="white"
                ),
            ],
            alignment="center",
            spacing=10,
        )

    @staticmethod
    def crear_instrucciones():
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
    def crear_tarjeta_estadistica(titulo: str, valor: Any, icono: str, color: str = "blue"):
        """Crea una tarjeta de estadística individual"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icono, color=color, size=30),
                    ft.Text(str(valor), size=20, weight="bold"),
                    ft.Text(titulo, size=12, color="gray")
                ], horizontal_alignment="center", spacing=5),
                padding=15,
                width=120
            ),
            elevation=3
        )