# controladores/controlador_juego.py
import time
from interfaz import MinesweeperGame

class ControladorJuego:
    def __init__(self, dao_partida):
        self.dao_partida = dao_partida
        self._juego_actual = None
        self.tiempo_inicio_juego = None

    @property
    def juego_actual(self):
        """Propiedad de solo lectura para el juego actual"""
        return self._juego_actual

    def reiniciar_juego(self):
        """Reinicia el juego actual"""
        self._juego_actual = None
        self.tiempo_inicio_juego = None

    def iniciar_nueva_partida(self, filas, columnas, minas, dificultad, usuario_id=None):
        """Inicia una nueva partida de buscaminas"""
        try:
            self._juego_actual = MinesweeperGame(filas, columnas, minas)
            self.tiempo_inicio_juego = time.time()
            
            # Guardar información de la partida si hay usuario
            if usuario_id:
                self.dao_partida.guardar_partida({
                    'usuario_id': usuario_id,
                    'dificultad': dificultad,
                    'filas': filas,
                    'columnas': columnas,
                    'minas': minas,
                    'fecha_inicio': self.tiempo_inicio_juego,
                    'estado': 'en_curso'
                })
            
            return True, "Juego iniciado correctamente"
        except Exception as e:
            return False, f"Error al iniciar juego: {str(e)}"

    def revelar_celda(self, fila, columna):
        """Revela una celda del tablero"""
        if not self._juego_actual:
            return False, False
        
        try:
            exito = self._juego_actual.revelar_celda(fila, columna)
            juego_terminado = self._juego_actual.juego_terminado
            
            return exito, juego_terminado
        except Exception as e:
            print(f"Error revelando celda: {e}")
            return False, False

    def alternar_bandera(self, fila, columna):
        """Coloca o quita una bandera en una celda"""
        if not self._juego_actual:
            return False
        
        try:
            return self._juego_actual.alternar_bandera(fila, columna)
        except Exception as e:
            print(f"Error alternando bandera: {e}")
            return False

    def obtener_estado(self):
        """Obtiene el estado actual del juego"""
        if not self._juego_actual:
            return {
                'filas': 0,
                'columnas': 0,
                'tablero': [],
                'reveladas': [],
                'banderas': [],
                'minas_restantes': 0,
                'dificultad': 'No seleccionada',
                'juego_terminado': False,
                'partida_ganada': False
            }
        
        return {
            'filas': self._juego_actual.filas,
            'columnas': self._juego_actual.columnas,
            'tablero': self._juego_actual.tablero,
            'reveladas': self._juego_actual.reveladas,
            'banderas': self._juego_actual.banderas,
            'minas_restantes': self._juego_actual.minas_restantes,
            'juego_terminado': self._juego_actual.juego_terminado,
            'partida_ganada': self._juego_actual.partida_ganada
        }

    def obtener_minas_restantes(self):
        """Obtiene el número de minas restantes por marcar"""
        if not self._juego_actual:
            return 0
        return self._juego_actual.minas_restantes

    def obtener_dificultad(self):
        """Obtiene la dificultad del juego actual"""
        if not self._juego_actual:
            return "No seleccionada"
        return "Personalizada"  # O puedes pasar la dificultad como parámetro

    def guardar_partida_actual(self, usuario_id, resultado, duracion):
        """Guarda la partida actual en la base de datos"""
        if not self._juego_actual or not self.tiempo_inicio_juego:
            return False
        
        try:
            partida_data = {
                'usuario_id': usuario_id,
                'dificultad': self.obtener_dificultad(),
                'filas': self._juego_actual.filas,
                'columnas': self._juego_actual.columnas,
                'minas': self._juego_actual.minas_totales,
                'fecha_inicio': self.tiempo_inicio_juego,
                'duracion': duracion,
                'resultado': resultado,
                'estado': 'completada'
            }
            
            self.dao_partida.guardar_partida(partida_data)
            return True
        except Exception as e:
            print(f"Error guardando partida: {e}")
            return False