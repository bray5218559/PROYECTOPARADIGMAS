# controladores/controlador_usuario.py
from typing import Dict, Any, Optional
from modelos.basedatos_json import UsuarioDAO
from modelos.entidades import Usuario
from modelos.clases_abstractas import ControladorAbstracto


    
class ControladorUsuario(ControladorAbstracto):
    def __init__(self, dao_usuario: UsuarioDAO):
        self._dao_usuario = dao_usuario
        self._usuario_actual: Optional[Usuario] = None

    def iniciar_sesion(self, nombre_usuario: str) -> tuple[bool, str]:
        """Intenta iniciar sesión con un usuario existente"""
        if not nombre_usuario.strip():
            return False, "El nombre de usuario es requerido"
        
        usuario = self._dao_usuario.obtener_usuario_por_nombre(nombre_usuario)
        if usuario:
            self._usuario_actual = usuario
            return True, f"¡Bienvenido de nuevo, {nombre_usuario}!"
        else:
            return False, f"Usuario '{nombre_usuario}' no encontrado. Regístrese primero."

    def registrar(self, nombre_usuario: str, correo: str = None) -> tuple[bool, str]:
        """Registra un nuevo usuario"""
        if not nombre_usuario.strip():
            return False, "El nombre de usuario es requerido"
        
        # Verificar si el usuario ya existe
        usuario_existente = self._dao_usuario.obtener_usuario_por_nombre(nombre_usuario)
        if usuario_existente:
            return False, f"El usuario '{nombre_usuario}' ya existe. Use otro nombre."
        
        try:
            # Crear nuevo usuario
            usuario = Usuario(
                id=None,
                nombre_usuario=nombre_usuario.strip(),
                correo=correo.strip() if correo else None,
                fecha_creacion="",  # Se establecerá en el DAO
                partidas_totales=0,
                partidas_ganadas=0
            )
            
            id_usuario = self._dao_usuario.guardar(usuario)
            self._usuario_actual = self._dao_usuario.obtener_por_id(id_usuario)
            return True, f"¡Usuario '{nombre_usuario}' registrado con éxito!"
            
        except Exception as e:
            return False, f"Error al registrar usuario: {str(e)}"

    def obtener_usuario_actual(self) -> Optional[Usuario]:
        """Obtiene el usuario actual"""
        return self._usuario_actual

    def actualizar_estadisticas_usuario(self, partida_ganada: bool, duracion: int, dificultad: str):
        """Actualiza las estadísticas del usuario actual"""
        if self._usuario_actual:
            self._dao_usuario.actualizar_estadisticas_usuario(
                self._usuario_actual.id, 
                partida_ganada, 
                duracion, 
                dificultad
            )
            # Refrescar datos del usuario
            self._usuario_actual = self._dao_usuario.obtener_por_id(self._usuario_actual.id)

    def obtener_estado(self) -> dict:
        """Obtiene las estadísticas del usuario actual en formato de diccionario"""
        if not self._usuario_actual:
            return {}
        
        partidas_totales = self._usuario_actual.partidas_totales
        partidas_ganadas = self._usuario_actual.partidas_ganadas
        partidas_perdidas = partidas_totales - partidas_ganadas
        porcentaje_victorias = (partidas_ganadas / partidas_totales * 100) if partidas_totales > 0 else 0
        
        return {
            'nombre_usuario': self._usuario_actual.nombre_usuario,
            'partidas_totales': partidas_totales,
            'partidas_ganadas': partidas_ganadas,
            'partidas_perdidas': partidas_perdidas,
            'porcentaje_victorias': round(porcentaje_victorias, 1),
            'mejor_tiempo_facil': getattr(self._usuario_actual, 'mejor_tiempo_facil', None),
            'mejor_tiempo_medio': getattr(self._usuario_actual, 'mejor_tiempo_medio', None),
            'mejor_tiempo_dificil': getattr(self._usuario_actual, 'mejor_tiempo_dificil', None)
        }

    @property
    def usuario_actual(self) -> Optional[Usuario]:
        return self._usuario_actual

    
    def obtener_estado(self) -> Dict[str, Any]:
        """Obtiene el estado actual del usuario con estadísticas"""
        if not self.usuario_actual:
            return {
                'nombre_usuario': 'Invitado',
                'partidas_totales': 0,
                'partidas_ganadas': 0,
                'partidas_perdidas': 0,
                'porcentaje_victorias': 0,
                'mejores_tiempos': {}
            }
        
        # Obtener estadísticas del usuario
        partidas = self.dao_usuario.obtener_partidas_usuario(self.usuario_actual.id)
        partidas_totales = len(partidas)
        partidas_ganadas = len([p for p in partidas if p.get('ganada')])
        partidas_perdidas = partidas_totales - partidas_ganadas
        
        porcentaje_victorias = 0
        if partidas_totales > 0:
            porcentaje_victorias = round((partidas_ganadas / partidas_totales) * 100, 1)
        
        # Calcular mejores tiempos por dificultad
        mejores_tiempos = self._calcular_mejores_tiempos(partidas)
        
        return {
            'nombre_usuario': self.usuario_actual.nombre,
            'partidas_totales': partidas_totales,
            'partidas_ganadas': partidas_ganadas,
            'partidas_perdidas': partidas_perdidas,
            'porcentaje_victorias': porcentaje_victorias,
            'mejores_tiempos': mejores_tiempos
        }
    
    def _calcular_mejores_tiempos(self, partidas):
        """Calcula los mejores tiempos por dificultad"""
        tiempos_por_dificultad = {'facil': [], 'medio': [], 'dificil': []}
        
        for partida in partidas:
            if partida.get('ganada') and partida.get('duracion'):
                dificultad = partida.get('dificultad', '').lower()
                if 'facil' in dificultad:
                    tiempos_por_dificultad['facil'].append(partida['duracion'])
                elif 'medio' in dificultad:
                    tiempos_por_dificultad['medio'].append(partida['duracion'])
                elif 'dificil' in dificultad:
                    tiempos_por_dificultad['dificil'].append(partida['duracion'])
        
        mejores_tiempos = {}
        for dificultad, tiempos in tiempos_por_dificultad.items():
            if tiempos:
                mejores_tiempos[dificultad] = min(tiempos)
            else:
                mejores_tiempos[dificultad] = "N/A"
        
        return mejores_tiempos