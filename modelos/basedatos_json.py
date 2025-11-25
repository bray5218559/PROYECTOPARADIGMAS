# modelos/basedatos_json.py
import json
import os
from typing import List, Optional, Dict, Any, Iterator
from datetime import datetime
from modelos.entidades import Usuario, Partida
from modelos.clases_abstractas import DAOAbstracto

class ExcepcionBaseDatos(Exception):
    """Excepción personalizada para errores de base de datos"""
    pass

class IteradorUsuarios:
    """Iterador para recorrer usuarios"""
    def __init__(self, usuarios: Dict[str, Any]):
        self.usuarios = list(usuarios.values())
        self.indice = 0
    
    def __iter__(self):
        return self
    
    def __next__(self) -> Usuario:
        if self.indice >= len(self.usuarios):
            raise StopIteration
        usuario = Usuario.desde_diccionario(self.usuarios[self.indice])
        self.indice += 1
        return usuario

class BaseDatosJSON:
    def __init__(self, ruta_base_datos: str = "datos"):
        self._ruta_base_datos = ruta_base_datos
        self._archivo_usuarios = os.path.join(ruta_base_datos, "usuarios.json")
        self._archivo_partidas = os.path.join(ruta_base_datos, "partidas.json")
        self._inicializar_base_datos()

    def _inicializar_base_datos(self):
        """Inicializa la base de datos JSON"""
        try:
            # Crear directorio si no existe
            if not os.path.exists(self._ruta_base_datos):
                os.makedirs(self._ruta_base_datos)
            
            # Crear archivo de usuarios si no existe
            if not os.path.exists(self._archivo_usuarios):
                with open(self._archivo_usuarios, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
            
            # Crear archivo de partidas si no existe
            if not os.path.exists(self._archivo_partidas):
                with open(self._archivo_partidas, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ExcepcionBaseDatos(f"Error al inicializar base de datos: {e}")

    def _leer_usuarios(self) -> Dict[str, Any]:
        """Lee todos los usuarios del archivo JSON"""
        try:
            with open(self._archivo_usuarios, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ExcepcionBaseDatos(f"Error al leer usuarios: {e}")

    def _escribir_usuarios(self, usuarios: Dict[str, Any]):
        """Escribe usuarios en el archivo JSON"""
        try:
            with open(self._archivo_usuarios, 'w', encoding='utf-8') as f:
                json.dump(usuarios, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ExcepcionBaseDatos(f"Error al escribir usuarios: {e}")

    def _leer_partidas(self) -> Dict[str, Any]:
        """Lee todas las partidas del archivo JSON"""
        try:
            with open(self._archivo_partidas, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ExcepcionBaseDatos(f"Error al leer partidas: {e}")

    def _escribir_partidas(self, partidas: Dict[str, Any]):
        """Escribe partidas en el archivo JSON"""
        try:
            with open(self._archivo_partidas, 'w', encoding='utf-8') as f:
                json.dump(partidas, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ExcepcionBaseDatos(f"Error al escribir partidas: {e}")

class UsuarioDAO(DAOAbstracto):
    def __init__(self, base_datos: BaseDatosJSON):
        self._base_datos = base_datos

    def guardar(self, usuario: Usuario) -> int:
        """Crea un nuevo usuario"""
        usuarios = self._base_datos._leer_usuarios()
        
        # Generar ID único
        ids_usuarios = [int(uid) for uid in usuarios.keys()] if usuarios else [0]
        nuevo_id = max(ids_usuarios) + 1 if ids_usuarios else 1
        
        # Convertir usuario a dict
        dict_usuario = usuario.a_diccionario()
        dict_usuario['id'] = nuevo_id
        dict_usuario['fecha_creacion'] = datetime.now().isoformat()
        
        # Guardar usuario
        usuarios[str(nuevo_id)] = dict_usuario
        self._base_datos._escribir_usuarios(usuarios)
        
        return nuevo_id

    def obtener_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        usuarios = self._base_datos._leer_usuarios()
        datos_usuario = usuarios.get(str(id_usuario))
        
        if datos_usuario:
            return Usuario.desde_diccionario(datos_usuario)
        return None

    def obtener_usuario_por_nombre(self, nombre_usuario: str) -> Optional[Usuario]:
        """Obtiene un usuario por nombre de usuario"""
        usuarios = self._base_datos._leer_usuarios()
        
        for datos_usuario in usuarios.values():
            if datos_usuario['nombre_usuario'].lower() == nombre_usuario.lower():
                return Usuario.desde_diccionario(datos_usuario)
        
        return None

    def actualizar_estadisticas_usuario(self, id_usuario: int, partida_ganada: bool, duracion: int, dificultad: str):
        """Actualiza las estadísticas del usuario después de una partida"""
        usuarios = self._base_datos._leer_usuarios()
        clave_usuario = str(id_usuario)
        
        if clave_usuario in usuarios:
            datos_usuario = usuarios[clave_usuario]
            
            # Actualizar estadísticas
            datos_usuario['partidas_totales'] = datos_usuario.get('partidas_totales', 0) + 1
            
            if partida_ganada:
                datos_usuario['partidas_ganadas'] = datos_usuario.get('partidas_ganadas', 0) + 1
            
            # Actualizar mejor tiempo si corresponde
            campo_mejor_tiempo = f"mejor_tiempo_{dificultad.lower()}"
            mejor_actual = datos_usuario.get(campo_mejor_tiempo)
            
            if partida_ganada and (mejor_actual is None or duracion < mejor_actual):
                datos_usuario[campo_mejor_tiempo] = duracion
            
            usuarios[clave_usuario] = datos_usuario
            self._base_datos._escribir_usuarios(usuarios)

    def obtener_clasificacion(self, dificultad: str, limite: int = 10) -> List[tuple]:
        """Obtiene el ranking de mejores tiempos para una dificultad"""
        usuarios = self._base_datos._leer_usuarios()
        campo_mejor_tiempo = f"mejor_tiempo_{dificultad.lower()}"
        
        clasificacion = []
        for datos_usuario in usuarios.values():
            mejor_tiempo = datos_usuario.get(campo_mejor_tiempo)
            if mejor_tiempo is not None:
                clasificacion.append((datos_usuario['nombre_usuario'], mejor_tiempo))
        
        # Ordenar por mejor tiempo (ascendente)
        clasificacion.sort(key=lambda x: x[1])
        return clasificacion[:limite]

    def iterar_usuarios(self) -> IteradorUsuarios:
        """Retorna un iterador para recorrer todos los usuarios"""
        usuarios = self._base_datos._leer_usuarios()
        return IteradorUsuarios(usuarios)

class PartidaDAO(DAOAbstracto):
    def __init__(self, base_datos: BaseDatosJSON):
        self._base_datos = base_datos

    def guardar(self, partida: Partida) -> int:
        """Guarda una partida y retorna su ID"""
        partidas = self._base_datos._leer_partidas()
        
        # Generar ID único
        ids_partidas = [int(pid) for pid in partidas.keys()] if partidas else [0]
        nuevo_id = max(ids_partidas) + 1 if ids_partidas else 1
        
        # Convertir partida a dict
        dict_partida = partida.a_diccionario()
        dict_partida['id'] = nuevo_id
        
        # Guardar partida
        partidas[str(nuevo_id)] = dict_partida
        self._base_datos._escribir_partidas(partidas)
        
        return nuevo_id

    def obtener_por_id(self, id_partida: int) -> Optional[Partida]:
        """Carga una partida por ID"""
        partidas = self._base_datos._leer_partidas()
        datos_partida = partidas.get(str(id_partida))
        
        if datos_partida:
            return Partida.desde_diccionario(datos_partida)
        return None

    def actualizar_resultado_partida(self, id_partida: int, partida_ganada: bool, duracion: int):
        """Actualiza el resultado final de una partida"""
        partidas = self._base_datos._leer_partidas()
        clave_partida = str(id_partida)
        
        if clave_partida in partidas:
            datos_partida = partidas[clave_partida]
            datos_partida['tiempo_fin'] = datetime.now().isoformat()
            datos_partida['segundos_duracion'] = duracion
            datos_partida['partida_ganada'] = partida_ganada
            datos_partida['partida_terminada'] = True
            
            partidas[clave_partida] = datos_partida
            self._base_datos._escribir_partidas(partidas)