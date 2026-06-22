# helpers/db_helper.py
from typing import List, Optional
from sqlalchemy.orm import Session

# Правильные импорты
from db_requester.movies import MovieDBModel
from db_models.user import UserDBModel


class DBHelper:
    """Класс с методами для работы с БД в тестах"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    # ============ Методы для пользователей ============

    def create_test_user(self, user_data: dict) -> UserDBModel:
        """Создает тестового пользователя"""
        user = UserDBModel(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[UserDBModel]:
        """Получает пользователя по ID"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[UserDBModel]:
        """Получает пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        self.db_session.delete(user)
        self.db_session.commit()

    # ============ Методы для фильмов ============

    def create_test_movie(self, movie_data: dict) -> MovieDBModel:
        """Создает тестовый фильм"""
        movie = MovieDBModel(**movie_data)
        self.db_session.add(movie)
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    def get_movie_by_id(self, movie_id: int) -> Optional[MovieDBModel]:
        """Получает фильм по ID"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()

    def get_movie_by_name(self, name: str) -> Optional[MovieDBModel]:
        """Получает фильм по названию"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).first()

    def get_all_movies(self, limit: int = 10) -> List[MovieDBModel]:
        """Получает все фильмы с ограничением по количеству"""
        result = self.db_session.query(MovieDBModel).limit(limit).all()
        return result  # type: ignore

    def delete_movie(self, movie: MovieDBModel):
        """Удаляет фильм"""
        self.db_session.delete(movie)
        self.db_session.commit()

    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()

    def movie_exists_by_id(self, movie_id: int) -> bool:
        """Проверяет существование фильма по ID"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).count() > 0

    def movie_exists_by_name(self, name: str) -> bool:
        """Проверяет существование фильма по названию"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).count() > 0

    def get_movie_count(self) -> int:
        """Возвращает общее количество фильмов в БД"""
        return self.db_session.query(MovieDBModel).count()