# controladores/controlador_juego.py
import time
from typing import Dict, Any, Tuple
from datetime import datetime
from typing import Optional
from modelos.logica_juego import Buscaminas, ExcepcionJuego
from modelos.basedatos_json import PartidaDAO
from modelos.entidades import Partida as EntidadPartida
from modelos.clases_abstractas import ControladorAbstracto

class ControladorJuego:
    def __init__(self, dao_partida):
        self.dao_partida = dao_partida
        self.juego_actual = None
        self.tiempo_inicio_juego = None
    
    def iniciar_nueva_partida(self, filas: int, columnas: int, minas: int, dificultad: str, id_usuario: int = None):
        """Inicia una nueva partida"""
        from modelos.juego import JuegoBuscaminas
        
        self.juego_actual = JuegoBuscaminas(filas, columnas, minas)
        self.juego_actual.inicializar_tablero()
        self.tiempo_inicio_juego = time.time()
        
        # Guardar referencia de la partida si hay usuario
        if id_usuario:
            self.partida_actual_id = self.dao_partida.crear_partida(
                id_usuario, dificultad, filas, columnas, minas
            )
    
    def revelar_celda(self, fila: int, columna: int) -> Tuple[bool, bool]:
        """Revela una celda y retorna (éxito, juego_terminado)"""
        if not self.juego_actual:
            return False, False
            
        exito = self.juego_actual.revelar_celda(fila, columna)
        juego_terminado = self.juego_actual.partida_ganada or self.juego_actual.partida_perdida
        
        return exito, juego_terminado
    
    def alternar_bandera(self, fila: int, columna: int) -> bool:
        """Coloca o quita una bandera en una celda"""
        if not self.juego_actual:
            return False
            
        return self.juego_actual.alternar_bandera(fila, columna)
    
    def obtener_estado(self) -> Dict[str, Any]:
        """Obtiene el estado actual del juego"""
        if not self.juego_actual:
            return {"tablero": [], "juego_activo": False}
            
        return {
            "tablero": self.juego_actual.tablero,
            "juego_activo": not (self.juego_actual.partida_ganada or self.juego_actual.partida_perdida),
            "partida_ganada": self.juego_actual.partida_ganada,
            "partida_perdida": self.juego_actual.partida_perdida
        }
    
    def obtener_minas_restantes(self) -> int:
        """Obtiene el número de minas restantes por marcar"""
        if not self.juego_actual:
            return 0
            
        return self.juego_actual.obtener_minas_restantes()
    
    def obtener_dificultad(self) -> str:
        """Obtiene la dificultad actual"""
        if not self.juego_actual:
            return "No seleccionada"
        
        minas = self.juego_actual.minas
        if minas == 10:
            return "Fácil"
        elif minas == 30:
            return "Medio"
        elif minas == 60:
            return "Difícil"
        else:
            return "Personalizada"

class ControladorJuego(ControladorAbstracto):
    def __init__(self, dao_partida: PartidaDAO):
        self._dao_partida = dao_partida
        self._juego_actual: Optional[Buscaminas] = None
        self._id_juego_actual: Optional[int] = None
        self._tiempo_inicio_juego: Optional[float] = None
        self._nivel_dificultad: str = "Fácil"

    def iniciar_nueva_partida(self, filas: int, columnas: int, minas: int, dificultad: str, id_usuario: Optional[int] = None):
        """Inicia una nueva partida"""
        try:
            self._juego_actual = Buscaminas(filas, columnas, minas)
            self._nivel_dificultad = dificultad
            
            # Crear entidad de partida para la base de datos
            partida_entidad = EntidadPartida(
                id=None,
                id_usuario=id_usuario,
                dificultad=dificultad,
                filas=filas,
                columnas=columnas,
                minas=minas,
                estado_tablero=self._juego_actual.obtener_estado()['tablero'],
                estado_revelado=self._juego_actual.obtener_estado()['revelado'],
                estado_banderas=self._juego_actual.obtener_estado()['banderas'],
                tiempo_inicio=datetime.now().isoformat()
            )
            
            # Guardar en base de datos
            self._id_juego_actual = self._dao_partida.guardar(partida_entidad)
            self._tiempo_inicio_juego = time.time()
            
            return self._juego_actual
        except ExcepcionJuego as e:
            raise ExcepcionJuego(f"Error al iniciar partida: {e}")

    def revelar_celda(self, fila: int, columna: int) -> tuple[bool, bool]:
        """Revela una celda y retorna (éxito, juego_terminado)"""
        if not self._juego_actual or self._juego_actual.partida_terminada or self._juego_actual.partida_ganada:
            return True, False
        
        try:
            exito = self._juego_actual.revelar(fila, columna)
            
            if not exito:  # Click en mina
                self._juego_actual._partida_terminada = True
                self._guardar_resultado_partida(False)
                return False, True
            elif self._juego_actual.partida_ganada:
                self._guardar_resultado_partida(True)
                return True, True
            
            return True, False
        except ExcepcionJuego as e:
            raise ExcepcionJuego(f"Error al revelar celda: {e}")

    def alternar_bandera(self, fila: int, columna: int):
        """Alterna bandera en una celda"""
        if self._juego_actual and not self._juego_actual.partida_terminada and not self._juego_actual.partida_ganada:
            try:
                self._juego_actual.alternar_bandera(fila, columna)
            except ExcepcionJuego as e:
                raise ExcepcionJuego(f"Error al alternar bandera: {e}")

    def _guardar_resultado_partida(self, partida_ganada: bool):
        """Guarda el resultado final del juego"""
        if self._id_juego_actual and self._tiempo_inicio_juego:
            duracion = int(time.time() - self._tiempo_inicio_juego)
            self._dao_partida.actualizar_resultado_partida(self._id_juego_actual, partida_ganada, duracion)

    def obtener_estado(self) -> dict:
        """Obtiene el estado actual del juego para la vista"""
        if not self._juego_actual:
            return {}
        
        return self._juego_actual.obtener_estado()

    def obtener_minas_restantes(self) -> int:
        """Calcula minas restantes basado en banderas"""
        if not self._juego_actual:
            return 0
        
        estado = self._juego_actual.obtener_estado()
        contador_banderas = sum(sum(1 for celda in fila if celda) for fila in estado['banderas'])
        return self._juego_actual.minas - contador_banderas

    def obtener_dificultad(self) -> str:
        """Retorna la dificultad actual"""
        return self._nivel_dificultad

    @property
    def juego_actual(self) -> Optional[Buscaminas]:
        return self._juego_actual

    @property
    def tiempo_inicio_juego(self) -> Optional[float]:
        return self._tiempo_inicio_juego