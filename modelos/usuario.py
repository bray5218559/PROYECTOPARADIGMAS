import uuid
from datetime import datetime

class Usuario:
    def __init__(self, nombre_usuario, correo=None):
        self.id = str(uuid.uuid4())
        self.nombre_usuario = nombre_usuario
        self.correo = correo
        self.fecha_registro = datetime.now().isoformat()
        
        # Estadísticas
        self.partidas_jugadas = 0
        self.partidas_ganadas = 0
        self.partidas_perdidas = 0
        self.tiempo_total_jugado = 0  # en segundos
        self.estadisticas_por_dificultad = {}  # {'Fácil': {partidas: X, ganadas: Y, mejor_tiempo: Z}}

    def to_dict(self):
        """Convierte el usuario a diccionario para guardar en JSON"""
        return {
            'id': self.id,
            'nombre_usuario': self.nombre_usuario,
            'correo': self.correo,
            'fecha_registro': self.fecha_registro,
            'partidas_jugadas': self.partidas_jugadas,
            'partidas_ganadas': self.partidas_ganadas,
            'partidas_perdidas': self.partidas_perdidas,
            'tiempo_total_jugado': self.tiempo_total_jugado,
            'estadisticas_por_dificultad': self.estadisticas_por_dificultad
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un usuario desde un diccionario"""
        usuario = cls(data['nombre_usuario'], data.get('correo'))
        usuario.id = data['id']
        usuario.fecha_registro = data['fecha_registro']
        usuario.partidas_jugadas = data['partidas_jugadas']
        usuario.partidas_ganadas = data['partidas_ganadas']
        usuario.partidas_perdidas = data['partidas_perdidas']
        usuario.tiempo_total_jugado = data['tiempo_total_jugado']
        usuario.estadisticas_por_dificultad = data.get('estadisticas_por_dificultad', {})
        return usuario