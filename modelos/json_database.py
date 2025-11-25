# modelos/json_database.py
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from modelos.entidades import User, Game
from modelos.abstract_classes import AbstractDAO

class JSONDatabase:
    def __init__(self, db_path: str = "data"):
        self.db_path = db_path
        self.users_file = os.path.join(db_path, "users.json")
        self.games_file = os.path.join(db_path, "games.json")
        self.init_database()

    def init_database(self):
        """Inicializa la base de datos JSON"""
        # Crear directorio si no existe
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        
        # Crear archivo de usuarios si no existe
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        # Crear archivo de juegos si no existe
        if not os.path.exists(self.games_file):
            with open(self.games_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def _read_users(self) -> Dict[str, Any]:
        """Lee todos los usuarios del archivo JSON"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_users(self, users: Dict[str, Any]):
        """Escribe usuarios en el archivo JSON"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    def _read_games(self) -> Dict[str, Any]:
        """Lee todos los juegos del archivo JSON"""
        try:
            with open(self.games_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_games(self, games: Dict[str, Any]):
        """Escribe juegos en el archivo JSON"""
        with open(self.games_file, 'w', encoding='utf-8') as f:
            json.dump(games, f, ensure_ascii=False, indent=2)

class UserDAO(AbstractDAO):
    def __init__(self, db: JSONDatabase):
        self.db = db

    def save(self, user: User) -> int:
        """Crea un nuevo usuario"""
        users = self.db._read_users()
        
        # Generar ID único
        user_ids = [int(uid) for uid in users.keys()] if users else [0]
        new_id = max(user_ids) + 1 if user_ids else 1
        
        # Convertir usuario a dict
        user_dict = user.to_dict()
        user_dict['id'] = new_id
        user_dict['created_at'] = datetime.now().isoformat()
        
        # Guardar usuario
        users[str(new_id)] = user_dict
        self.db._write_users(users)
        
        return new_id

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID"""
        users = self.db._read_users()
        user_data = users.get(str(user_id))
        
        if user_data:
            return User.from_dict(user_data)
        return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por nombre de usuario"""
        users = self.db._read_users()
        
        for user_data in users.values():
            if user_data['username'].lower() == username.lower():
                return User.from_dict(user_data)
        
        return None

    def update_user_stats(self, user_id: int, game_won: bool, duration: int, difficulty: str):
        """Actualiza las estadísticas del usuario después de una partida"""
        users = self.db._read_users()
        user_key = str(user_id)
        
        if user_key in users:
            user_data = users[user_key]
            
            # Actualizar estadísticas
            user_data['total_games'] = user_data.get('total_games', 0) + 1
            
            if game_won:
                user_data['games_won'] = user_data.get('games_won', 0) + 1
            
            # Actualizar mejor tiempo si corresponde
            best_time_field = f"best_time_{difficulty.lower()}"
            current_best = user_data.get(best_time_field)
            
            if game_won and (current_best is None or duration < current_best):
                user_data[best_time_field] = duration
            
            users[user_key] = user_data
            self.db._write_users(users)

    def get_leaderboard(self, difficulty: str, limit: int = 10) -> List[tuple]:
        """Obtiene el ranking de mejores tiempos para una dificultad"""
        users = self.db._read_users()
        best_time_field = f"best_time_{difficulty.lower()}"
        
        leaderboard = []
        for user_data in users.values():
            best_time = user_data.get(best_time_field)
            if best_time is not None:
                leaderboard.append((user_data['username'], best_time))
        
        # Ordenar por mejor tiempo (ascendente)
        leaderboard.sort(key=lambda x: x[1])
        return leaderboard[:limit]

class GameDAO(AbstractDAO):
    def __init__(self, db: JSONDatabase):
        self.db = db

    def save(self, game: Game) -> int:
        """Guarda una partida y retorna su ID"""
        games = self.db._read_games()
        
        # Generar ID único
        game_ids = [int(gid) for gid in games.keys()] if games else [0]
        new_id = max(game_ids) + 1 if game_ids else 1
        
        # Convertir juego a dict
        game_dict = game.to_dict()
        game_dict['id'] = new_id
        
        # Guardar juego
        games[str(new_id)] = game_dict
        self.db._write_games(games)
        
        return new_id

    def get_by_id(self, game_id: int) -> Optional[Game]:
        """Carga una partida por ID"""
        games = self.db._read_games()
        game_data = games.get(str(game_id))
        
        if game_data:
            return Game.from_dict(game_data)
        return None

    def update_game_result(self, game_id: int, game_won: bool, duration: int):
        """Actualiza el resultado final de una partida"""
        games = self.db._read_games()
        game_key = str(game_id)
        
        if game_key in games:
            game_data = games[game_key]
            game_data['end_time'] = datetime.now().isoformat()
            game_data['duration_seconds'] = duration
            game_data['game_won'] = game_won
            game_data['game_over'] = True
            
            games[game_key] = game_data
            self.db._write_games(games)