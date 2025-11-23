# modelos/entities.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json

@dataclass
class User:
    id: Optional[int]
    username: str
    email: Optional[str]
    created_at: str
    total_games: int = 0
    games_won: int = 0
    best_time_easy: Optional[int] = None
    best_time_medium: Optional[int] = None
    best_time_hard: Optional[int] = None

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'total_games': self.total_games,
            'games_won': self.games_won,
            'best_time_easy': self.best_time_easy,
            'best_time_medium': self.best_time_medium,
            'best_time_hard': self.best_time_hard
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            username=data['username'],
            email=data.get('email'),
            created_at=data['created_at'],
            total_games=data.get('total_games', 0),
            games_won=data.get('games_won', 0),
            best_time_easy=data.get('best_time_easy'),
            best_time_medium=data.get('best_time_medium'),
            best_time_hard=data.get('best_time_hard')
        )

@dataclass
class Game:
    id: Optional[int]
    user_id: Optional[int]
    difficulty: str
    rows: int
    cols: int
    mines: int
    board_state: List[List[int]]
    revealed_state: List[List[bool]]
    flagged_state: List[List[bool]]
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[int] = None
    game_won: bool = False
    game_over: bool = False

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'difficulty': self.difficulty,
            'rows': self.rows,
            'cols': self.cols,
            'mines': self.mines,
            'board_state': self.board_state,
            'revealed_state': self.revealed_state,
            'flagged_state': self.flagged_state,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_seconds': self.duration_seconds,
            'game_won': self.game_won,
            'game_over': self.game_over
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            difficulty=data['difficulty'],
            rows=data['rows'],
            cols=data['cols'],
            mines=data['mines'],
            board_state=data['board_state'],
            revealed_state=data['revealed_state'],
            flagged_state=data['flagged_state'],
            start_time=data['start_time'],
            end_time=data.get('end_time'),
            duration_seconds=data.get('duration_seconds'),
            game_won=data.get('game_won', False),
            game_over=data.get('game_over', False)
        )