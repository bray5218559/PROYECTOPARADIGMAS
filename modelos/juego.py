import random
from typing import List, Dict, Any

class JuegoBuscaminas:
    def __init__(self, filas: int, columnas: int, minas: int):
        self.filas = filas
        self.columnas = columnas
        self.minas = minas
        self.tablero = []
        self.partida_ganada = False
        self.partida_perdida = False
        self.celdas_reveladas = 0
        
    def inicializar_tablero(self):
        """Inicializa el tablero vacío"""
        self.tablero = []
        for fila in range(self.filas):
            fila_tablero = []
            for columna in range(self.columnas):
                fila_tablero.append({
                    "es_mina": False,
                    "revelada": False,
                    "bandera": False,
                    "minas_adyacentes": 0
                })
            self.tablero.append(fila_tablero)
        
        self._colocar_minas()
        self._calcular_minas_adyacentes()
        self.partida_ganada = False
        self.partida_perdida = False
        self.celdas_reveladas = 0
    
    def _colocar_minas(self):
        """Coloca las minas aleatoriamente en el tablero"""
        minas_colocadas = 0
        while minas_colocadas < self.minas:
            fila = random.randint(0, self.filas - 1)
            columna = random.randint(0, self.columnas - 1)
            
            if not self.tablero[fila][columna]["es_mina"]:
                self.tablero[fila][columna]["es_mina"] = True
                minas_colocadas += 1
    
    def _calcular_minas_adyacentes(self):
        """Calcula el número de minas adyacentes para cada celda"""
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if not self.tablero[fila][columna]["es_mina"]:
                    minas_adyacentes = self._contar_minas_adyacentes(fila, columna)
                    self.tablero[fila][columna]["minas_adyacentes"] = minas_adyacentes
    
    def _contar_minas_adyacentes(self, fila: int, columna: int) -> int:
        """Cuenta las minas en las celdas adyacentes"""
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                    
                nueva_fila, nueva_columna = fila + i, columna + j
                if (0 <= nueva_fila < self.filas and 
                    0 <= nueva_columna < self.columnas and 
                    self.tablero[nueva_fila][nueva_columna]["es_mina"]):
                    count += 1
        return count
    
    def revelar_celda(self, fila: int, columna: int) -> bool:
        """Revela una celda y sus adyacentes si es necesario"""
        if (fila < 0 or fila >= self.filas or 
            columna < 0 or columna >= self.columnas or
            self.tablero[fila][columna]["revelada"] or
            self.tablero[fila][columna]["bandera"] or
            self.partida_ganada or self.partida_perdida):
            return False
        
        celda = self.tablero[fila][columna]
        celda["revelada"] = True
        self.celdas_reveladas += 1
        
        # Si es mina, game over
        if celda["es_mina"]:
            self.partida_perdida = True
            self._revelar_todas_las_minas()
            return True
        
        # Si no tiene minas adyacentes, revelar celdas adyacentes
        if celda["minas_adyacentes"] == 0:
            self._revelar_celdas_adyacentes(fila, columna)
        
        # Verificar si ganó
        if self.celdas_reveladas == (self.filas * self.columnas - self.minas):
            self.partida_ganada = True
            self._marcar_todas_las_minas()
        
        return True
    
    def _revelar_celdas_adyacentes(self, fila: int, columna: int):
        """Revela recursivamente las celdas adyacentes"""
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                    
                nueva_fila, nueva_columna = fila + i, columna + j
                if (0 <= nueva_fila < self.filas and 
                    0 <= nueva_columna < self.columnas):
                    self.revelar_celda(nueva_fila, nueva_columna)
    
    def _revelar_todas_las_minas(self):
        """Revela todas las minas cuando se pierde"""
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.tablero[fila][columna]["es_mina"]:
                    self.tablero[fila][columna]["revelada"] = True
    
    def _marcar_todas_las_minas(self):
        """Marca todas las minas cuando se gana"""
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.tablero[fila][columna]["es_mina"]:
                    self.tablero[fila][columna]["bandera"] = True
    
    def alternar_bandera(self, fila: int, columna: int) -> bool:
        """Coloca o quita una bandera en una celda"""
        if (fila < 0 or fila >= self.filas or 
            columna < 0 or columna >= self.columnas or
            self.tablero[fila][columna]["revelada"] or
            self.partida_ganada or self.partida_perdida):
            return False
        
        self.tablero[fila][columna]["bandera"] = not self.tablero[fila][columna]["bandera"]
        return True
    
    def obtener_minas_restantes(self) -> int:
        """Calcula las minas restantes por marcar"""
        banderas_colocadas = 0
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.tablero[fila][columna]["bandera"]:
                    banderas_colocadas += 1
        
        return self.minas - banderas_colocadas