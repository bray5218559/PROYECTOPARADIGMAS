# controladores/user_controller.py
from typing import Optional
from modelos.json_database import UserDAO
from modelos.entidades import User
from modelos.abstract_classes import AbstractController

class UserController(AbstractController):
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
            return True, f"¡Bienvenido de nuevo, {username}!"
        else:
            return False, f"Usuario '{username}' no encontrado. Regístrese primero."

    def register(self, username: str, email: str = None) -> tuple[bool, str]:
        """Registra un nuevo usuario"""
        if not username.strip():
            return False, "El nombre de usuario es requerido"
        
        # Verificar si el usuario ya existe
        existing_user = self.user_dao.get_user_by_username(username)
        if existing_user:
            return False, f"El usuario '{username}' ya existe. Use otro nombre."
        
        try:
            # Crear nuevo usuario
            user = User(
                id=None,
                username=username.strip(),
                email=email.strip() if email else None,
                created_at="",  # Se establecerá en el DAO
                total_games=0,
                games_won=0
            )
            
            user_id = self.user_dao.save(user)
            self.current_user = self.user_dao.get_by_id(user_id)
            return True, f"¡Usuario '{username}' registrado con éxito!"
            
        except Exception as e:
            return False, f"Error al registrar usuario: {str(e)}"

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
            self.current_user = self.user_dao.get_by_id(self.current_user.id)

    def get_state(self) -> dict:
        """Obtiene las estadísticas del usuario actual en formato de diccionario"""
        if not self.current_user:
            return {}
        
        total_games = self.current_user.total_games
        games_won = self.current_user.games_won
        games_lost = total_games - games_won
        win_percentage = (games_won / total_games * 100) if total_games > 0 else 0
        
        # Usar getattr para manejar atributos que podrían no existir
        return {
            'username': self.current_user.username,
            'total_games': total_games,
            'games_won': games_won,
            'games_lost': games_lost,
            'win_percentage': round(win_percentage, 1),
            'best_time_easy': getattr(self.current_user, 'best_time_easy', None),
            'best_time_medium': getattr(self.current_user, 'best_time_medium', None),
            'best_time_hard': getattr(self.current_user, 'best_time_hard', None)
        }