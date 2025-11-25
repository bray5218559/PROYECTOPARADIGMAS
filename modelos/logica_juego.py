# modelos/logica_juego.py
import random
from typing import List, Tuple, Iterator
from modelos.clases_abstractas import JuegoAbstracto

class ExcepcionJuego(Exception):
    """Excepción personalizada para errores del juego"""
    pass

class IteradorTablero:
    """Iterador para recorrer el tablero"""
    def __init__(self, tablero: List[List[int]]):
        self.tablero = tablero
        self.fila_actual = 0
        self.columna_actual = 0
    
    def __iter__(self):
        return self
    
    def __next__(self) -> Tuple[int, int, int]:
        if self.fila_actual >= len(self.tablero):
            raise StopIteration
        
        valor = self.tablero[self.fila_actual][self.columna_actual]
        posicion = (self.fila_actual, self.columna_actual)
        
        self.columna_actual += 1
        if self.columna_actual >= len(self.tablero[0]):
            self.columna_actual = 0
            self.fila_actual += 1
        
        return (*posicion, valor)

class Buscaminas(JuegoAbstracto):
    def __init__(self, filas: int, columnas: int, minas: int):
        if minas >= filas * columnas:
            raise ExcepcionJuego("Demasiadas minas para el tamaño del tablero")
        
        self._filas = filas
        self._columnas = columnas
        self._minas = minas

        self._tablero = [[0 for _ in range(columnas)] for _ in range(filas)]
        self._revelado = [[False for _ in range(columnas)] for _ in range(filas)]
        self._banderas = [[False for _ in range(columnas)] for _ in range(filas)]

        self._partida_terminada = False
        self._partida_ganada = False
        self._primer_click = True
        self._posiciones_minas: List[Tuple[int, int]] = []

    @property
    def filas(self) -> int:
        return self._filas

    @property
    def columnas(self) -> int:
        return self._columnas

    @property
    def minas(self) -> int:
        return self._minas

    @property
    def partida_terminada(self) -> bool:
        return self._partida_terminada

    @property
    def partida_ganada(self) -> bool:
        return self._partida_ganada

    def _colocar_minas_despues_primer_click(self, fila: int, columna: int):
        """Coloca minas después del primer click para evitar perder inmediatamente"""
        posiciones = [(r, c) for r in range(self._filas) for c in range(self._columnas)]
        
        # Remover la posición del primer click y sus alrededores
        posiciones_seguras = set()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = fila + dr, columna + dc
                if 0 <= nr < self._filas and 0 <= nc < self._columnas:
                    posiciones_seguras.add((nr, nc))
        
        posiciones = [pos for pos in posiciones if pos not in posiciones_seguras]
        
        try:
            self._posiciones_minas = random.sample(posiciones, min(self._minas, len(posiciones)))
        except ValueError as e:
            raise ExcepcionJuego(f"No se pueden colocar las minas: {e}")

        self._tablero = [[0 for _ in range(self._columnas)] for _ in range(self._filas)]

        for r, c in self._posiciones_minas:
            self._tablero[r][c] = -1

        for r in range(self._filas):
            for c in range(self._columnas):
                if self._tablero[r][c] != -1:
                    self._tablero[r][c] = self._contar_minas_adyacentes(r, c)

    def _contar_minas_adyacentes(self, fila: int, columna: int) -> int:
        contador = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = fila + dr, columna + dc
                if 0 <= nr < self._filas and 0 <= nc < self._columnas:
                    if self._tablero[nr][nc] == -1:
                        contador += 1
        return contador

    def revelar(self, fila: int, columna: int) -> bool:
        if not (0 <= fila < self._filas and 0 <= columna < self._columnas):
            raise ExcepcionJuego("Posición fuera del tablero")
            
        if self._primer_click:
            self._colocar_minas_despues_primer_click(fila, columna)
            self._primer_click = False

        if self._banderas[fila][columna]:
            return True

        if self._tablero[fila][columna] == -1:
            self._partida_terminada = True
            return False

        if not self._revelado[fila][columna]:
            self._revelado[fila][columna] = True

            if self._tablero[fila][columna] == 0:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = fila + dr, columna + dc
                        if 0 <= nr < self._filas and 0 <= nc < self._columnas:
                            if not self._revelado[nr][nc] and not self._banderas[nr][nc]:
                                self.revelar(nr, nc)

        self.verificar_victoria()
        return True

    def alternar_bandera(self, fila: int, columna: int) -> None:
        if not (0 <= fila < self._filas and 0 <= columna < self._columnas):
            raise ExcepcionJuego("Posición fuera del tablero")
            
        if not self._revelado[fila][columna] and not self._partida_terminada and not self._partida_ganada:
            self._banderas[fila][columna] = not self._banderas[fila][columna]
            self.verificar_victoria()

    def verificar_victoria(self) -> None:
        # Verificar si todas las celdas no minadas están reveladas
        for r in range(self._filas):
            for c in range(self._columnas):
                if self._tablero[r][c] != -1 and not self._revelado[r][c]:
                    return
        self._partida_ganada = True
        self._partida_terminada = True

    def obtener_estado(self) -> dict:
        return {
            'tablero': self._tablero,
            'revelado': self._revelado,
            'banderas': self._banderas,
            'partida_terminada': self._partida_terminada,
            'partida_ganada': self._partida_ganada,
            'filas': self._filas,
            'columnas': self._columnas,
            'minas': self._minas
        }

    def iterar_tablero(self) -> IteradorTablero:
        """Retorna un iterador para recorrer el tablero"""
        return IteradorTablero(self._tablero)