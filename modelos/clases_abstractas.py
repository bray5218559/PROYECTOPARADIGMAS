# modelos/clases_abstractas.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class JuegoAbstracto(ABC):
    @abstractmethod
    def revelar(self, fila: int, columna: int) -> bool:
        pass
    
    @abstractmethod
    def alternar_bandera(self, fila: int, columna: int) -> None:
        pass
    
    @abstractmethod
    def verificar_victoria(self) -> None:
        pass

class ControladorAbstracto(ABC):
    @abstractmethod
    def obtener_estado(self) -> Dict[str, Any]:
        pass

class DAOAbstracto(ABC):
    @abstractmethod
    def guardar(self, entidad) -> int:
        pass
    
    @abstractmethod
    def obtener_por_id(self, id_entidad: int):
        pass