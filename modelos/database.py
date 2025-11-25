# modelos/database.py
import sqlite3
import json
from typing import List, Optional
from modelos.entidades import User, Game
from modelos.abstract_classes import AbstractDAO

class DatabaseManager:
    def __init__(self, db_path: str = "minesweeper.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    created_at TEXT NOT NULL,
                    total_games INTEGER DEFAULT 0,
                    games_won INTEGER DEFAULT 0,
                    best_time_easy INTEGER,
                    best_time_medium INTEGER,
                    best_time_hard INTEGER
                )
            ''')
            
            # Tabla de partidas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    difficulty TEXT NOT NULL,
                    rows INTEGER NOT NULL,
                    cols INTEGER NOT NULL,
                    mines INTEGER NOT NULL,
                    board_state TEXT NOT NULL,
                    revealed_state TEXT NOT NULL,
                    flagged_state TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_seconds INTEGER,
                    game_won BOOLEAN DEFAULT FALSE,
                    game_over BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()

    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)

class UserDAO(AbstractDAO):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save(self, user: User) -> int:
        """Crea un nuevo usuario"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            from datetime import datetime
            created_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO users (username, email, created_at)
                VALUES (?, ?, ?)
            ''', (user.username, user.email, created_at))
            
            return cursor.lastrowid

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_user(row)
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por nombre de usuario"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_user(row)
            return None

    def update_user_stats(self, user_id: int, game_won: bool, duration: int, difficulty: str):
        """Actualiza las estadísticas del usuario después de una partida"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT total_games, games_won, best_time_easy, best_time_medium, best_time_hard FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                total_games, games_won, best_easy, best_medium, best_hard = row
                total_games += 1
                if game_won:
                    games_won += 1
                
                # Actualizar mejor tiempo si corresponde
                best_time_field = f"best_time_{difficulty.lower()}"
                current_best = locals()[f"best_{difficulty.lower()}"]
                
                if game_won and (current_best is None or duration < current_best):
                    cursor.execute(f'''
                        UPDATE users 
                        SET total_games = ?, games_won = ?, {best_time_field} = ?
                        WHERE id = ?
                    ''', (total_games, games_won, duration, user_id))
                else:
                    cursor.execute('''
                        UPDATE users 
                        SET total_games = ?, games_won = ?
                        WHERE id = ?
                    ''', (total_games, games_won, user_id))

    def get_leaderboard(self, difficulty: str, limit: int = 10) -> List[tuple]:
        """Obtiene el ranking de mejores tiempos para una dificultad"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            best_time_field = f"best_time_{difficulty.lower()}"
            
            cursor.execute(f'''
                SELECT username, {best_time_field} 
                FROM users 
                WHERE {best_time_field} IS NOT NULL 
                ORDER BY {best_time_field} ASC 
                LIMIT ?
            ''', (limit,))
            
            return cursor.fetchall()

    def _row_to_user(self, row) -> User:
        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            created_at=row[3],
            total_games=row[4] or 0,
            games_won=row[5] or 0,
            best_time_easy=row[6],
            best_time_medium=row[7],
            best_time_hard=row[8]
        )

class GameDAO(AbstractDAO):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save(self, game: Game) -> int:
        """Guarda una partida y retorna su ID"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO games (
                    user_id, difficulty, rows, cols, mines, 
                    board_state, revealed_state, flagged_state,
                    start_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game.user_id,
                game.difficulty,
                game.rows,
                game.cols,
                game.mines,
                json.dumps(game.board_state),
                json.dumps(game.revealed_state),
                json.dumps(game.flagged_state),
                game.start_time
            ))
            
            return cursor.lastrowid

    def get_by_id(self, game_id: int) -> Optional[Game]:
        """Carga una partida por ID"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM games WHERE id = ?', (game_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_game(row)
            return None

    def update_game_result(self, game_id: int, game_won: bool, duration: int):
        """Actualiza el resultado final de una partida"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            from datetime import datetime
            end_time = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE games 
                SET end_time = ?, duration_seconds = ?, game_won = ?, game_over = TRUE
                WHERE id = ?
            ''', (end_time, duration, game_won, game_id))

    def _row_to_game(self, row) -> Game:
        return Game(
            id=row[0],
            user_id=row[1],
            difficulty=row[2],
            rows=row[3],
            cols=row[4],
            mines=row[5],
            board_state=json.loads(row[6]),
            revealed_state=json.loads(row[7]),
            flagged_state=json.loads(row[8]),
            start_time=row[9],
            end_time=row[10],
            duration_seconds=row[11],
            game_won=bool(row[12]),
            game_over=bool(row[13])
        )