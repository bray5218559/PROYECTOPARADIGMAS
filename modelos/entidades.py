# modelos/entidades.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Usuario:
    id: Optional[int]
    nombre_usuario: str
    correo: Optional[str]
    fecha_creacion: str
    partidas_totales: int = 0
    partidas_ganadas: int = 0
    mejor_tiempo_facil: Optional[int] = None
    mejor_tiempo_medio: Optional[int] = None
    mejor_tiempo_dificil: Optional[int] = None

    def a_diccionario(self):
        return {
            'id': self.id,
            'nombre_usuario': self.nombre_usuario,
            'correo': self.correo,
            'fecha_creacion': self.fecha_creacion,
            'partidas_totales': self.partidas_totales,
            'partidas_ganadas': self.partidas_ganadas,
            'mejor_tiempo_facil': self.mejor_tiempo_facil,
            'mejor_tiempo_medio': self.mejor_tiempo_medio,
            'mejor_tiempo_dificil': self.mejor_tiempo_dificil
        }

    @classmethod
    def desde_diccionario(cls, datos: dict):
        return cls(
            id=datos.get('id'),
            nombre_usuario=datos['nombre_usuario'],
            correo=datos.get('correo'),
            fecha_creacion=datos['fecha_creacion'],
            partidas_totales=datos.get('partidas_totales', 0),
            partidas_ganadas=datos.get('partidas_ganadas', 0),
            mejor_tiempo_facil=datos.get('mejor_tiempo_facil'),
            mejor_tiempo_medio=datos.get('mejor_tiempo_medio'),
            mejor_tiempo_dificil=datos.get('mejor_tiempo_dificil')
        )

@dataclass
class Partida:
    id: Optional[int]
    id_usuario: Optional[int]
    dificultad: str
    filas: int
    columnas: int
    minas: int
    estado_tablero: List[List[int]]
    estado_revelado: List[List[bool]]
    estado_banderas: List[List[bool]]
    tiempo_inicio: str
    tiempo_fin: Optional[str] = None
    segundos_duracion: Optional[int] = None
    partida_ganada: bool = False
    partida_terminada: bool = False

    def a_diccionario(self):
        return {
            'id': self.id,
            'id_usuario': self.id_usuario,
            'dificultad': self.dificultad,
            'filas': self.filas,
            'columnas': self.columnas,
            'minas': self.minas,
            'estado_tablero': self.estado_tablero,
            'estado_revelado': self.estado_revelado,
            'estado_banderas': self.estado_banderas,
            'tiempo_inicio': self.tiempo_inicio,
            'tiempo_fin': self.tiempo_fin,
            'segundos_duracion': self.segundos_duracion,
            'partida_ganada': self.partida_ganada,
            'partida_terminada': self.partida_terminada
        }

    @classmethod
    def desde_diccionario(cls, datos: dict):
        return cls(
            id=datos.get('id'),
            id_usuario=datos.get('id_usuario'),
            dificultad=datos['dificultad'],
            filas=datos['filas'],
            columnas=datos['columnas'],
            minas=datos['minas'],
            estado_tablero=datos['estado_tablero'],
            estado_revelado=datos['estado_revelado'],
            estado_banderas=datos['estado_banderas'],
            tiempo_inicio=datos['tiempo_inicio'],
            tiempo_fin=datos.get('tiempo_fin'),
            segundos_duracion=datos.get('segundos_duracion'),
            partida_ganada=datos.get('partida_ganada', False),
            partida_terminada=datos.get('partida_terminada', False)
        )