# controladores/user_controller.py
from modelos.database import UserDAO
from modelos.entities import User
from typing import Optional

class UserController:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao
        self.current_user: Optional[User] = None

    def login(self, username: str) -> tuple[bool, str]:
        """Intenta iniciar sesión con un usuario existente"""
        if not username.strip():
            return False, "El nombre de usuario es requerido"
        
        user = self.user_dao.get_user_by_username(username)
        if user:
            self.current_user = user
            return True, f"Bienvenido de nuevo, {username}!"
        else:
            return False, "Usuario no encontrado. Regístrese primero."

    def register(self, username: str, email: str = None) -> tuple[bool, str]:
        """Registra un nuevo usuario"""
        if not username.strip():
            return False, "El nombre de usuario es requerido"
        
        try:
            user = self.user_dao.create_user(username, email)
            self.current_user = user
            return True, f"¡Usuario {username} registrado con éxito!"
        except Exception as e:
            return False, "Error: El usuario ya existe"

    def get_current_user(self) -> Optional[User]:
        """Obtiene el usuario actual"""
        return self.current_user

    def update_user_stats(self, game_won: bool, duration: int, difficulty: str):
        """Actualiza las estadísticas del usuario actual"""
        if self.current_user:
            self.user_dao.update_user_stats(
                self.current_user.id, 
                game_won, 
                duration, 
                difficulty
            )
            # Refrescar datos del usuario
            self.current_user = self.user_dao.get_user(self.current_user.id)

    def get_user_stats(self) -> dict:
        """Obtiene las estadísticas del usuario actual en formato de diccionario"""
        if not self.current_user:
            return {}
        
        total_games = self.current_user.total_games
        win_percentage = (self.current_user.games_won / total_games * 100) if total_games > 0 else 0
        
        return {
            'username': self.current_user.username,
            'total_games': total_games,
            'games_won': self.current_user.games_won,
            'win_percentage': win_percentage,
            'best_time_easy': self.current_user.best_time_easy,
            'best_time_medium': self.current_user.best_time_medium,
            'best_time_hard': self.current_user.best_time_hard
        }