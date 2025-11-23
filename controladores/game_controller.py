# controladores/game_controller.py
import time
from datetime import datetime
from modelos.game_logic import MinesweeperGame
from modelos.database import GameDAO
from modelos.entities import Game as GameEntity
from typing import Optional

class GameController:
    def __init__(self, game_dao: GameDAO):
        self.game_dao = game_dao
        self.current_game: Optional[MinesweeperGame] = None
        self.current_game_id: Optional[int] = None
        self.game_start_time: Optional[float] = None
        self.difficulty_level: str = "Fácil"

    def start_new_game(self, rows: int, cols: int, mines: int, difficulty: str, user_id: Optional[int] = None):
        """Inicia una nueva partida"""
        self.current_game = MinesweeperGame(rows, cols, mines)
        self.difficulty_level = difficulty
        
        # Crear entidad de juego para la base de datos
        game_entity = GameEntity(
            id=None,
            user_id=user_id,
            difficulty=difficulty,
            rows=rows,
            cols=cols,
            mines=mines,
            board_state=self.current_game.board,
            revealed_state=self.current_game.revealed,
            flagged_state=self.current_game.flagged,
            start_time=datetime.now().isoformat()
        )
        
        # Guardar en base de datos
        self.current_game_id = self.game_dao.save_game(game_entity)
        self.game_start_time = time.time()
        
        return self.current_game

    def reveal_cell(self, row: int, col: int) -> tuple[bool, bool]:
        """Revela una celda y retorna (éxito, juego_terminado)"""
        if not self.current_game or self.current_game.game_over or self.current_game.game_won:
            return True, False
        
        success = self.current_game.reveal(row, col)
        
        if not success:  # Click en mina
            self.current_game.game_over = True
            self._save_game_result(False)
            return False, True
        elif self.current_game.game_won:
            self._save_game_result(True)
            return True, True
        
        return True, False

    def toggle_flag(self, row: int, col: int):
        """Alterna bandera en una celda"""
        if self.current_game and not self.current_game.game_over and not self.current_game.game_won:
            self.current_game.toggle_flag(row, col)

    def _save_game_result(self, game_won: bool):
        """Guarda el resultado final del juego"""
        if self.current_game_id and self.game_start_time:
            duration = int(time.time() - self.game_start_time)
            self.game_dao.update_game_result(self.current_game_id, game_won, duration)

    def get_game_state(self) -> dict:
        """Obtiene el estado actual del juego para la vista"""
        if not self.current_game:
            return {}
        
        return {
            'board': self.current_game.board,
            'revealed': self.current_game.revealed,
            'flagged': self.current_game.flagged,
            'game_over': self.current_game.game_over,
            'game_won': self.current_game.game_won,
            'rows': self.current_game.rows,
            'cols': self.current_game.cols,
            'mines': self.current_game.mines
        }

    def get_remaining_mines(self) -> int:
        """Calcula minas restantes basado en banderas"""
        if not self.current_game:
            return 0
        
        flagged_count = sum(sum(1 for flagged in row) for row in self.current_game.flagged)
        return self.current_game.mines - flagged_count

    def get_difficulty(self) -> str:
        """Retorna la dificultad actual"""
        return self.difficulty_level