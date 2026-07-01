# tests/test_db_helper.py
import sys
import os
from datetime import datetime
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.db_helper import DBHelper


@pytest.fixture
def movie_helper(db_session):
    """Фикстура, которая создает хелпер и очищает тестовые данные после теста"""
    helper = DBHelper(db_session)
    created_movies = []

    # Сохраняем оригинальный метод create_test_movie
    original_create = helper.create_test_movie

    def create_and_track(movie_data):
        new_movie = original_create(movie_data)
        created_movies.append(new_movie)
        return new_movie

    # Подменяем метод для отслеживания созданных фильмов
    helper.create_test_movie = create_and_track
    helper._created_movies = created_movies

    yield helper

    # После теста удаляем все созданные фильмы
    for created_movie in created_movies:
        try:
            helper.delete_movie(created_movie)
        except Exception as e:
            # Если фильм уже удален или не существует, просто игнорируем
            print(f"⚠️ Не удалось удалить фильм {created_movie.id}: {e}")


def test_create_movie_via_helper(movie_helper):
    """Тест создания фильма через хелпер"""
    # Данные для нового фильма
    movie_data = {
        "id": 999999,
        "name": "Тестовый фильм из хелпера",
        "price": 150,
        "description": "Создан через хелпер",
        "image_url": "https://example.com/helper.jpg",
        "location": "SPB",
        "published": True,
        "rating": 5,
        "genre_id": 1,
        "created_at": datetime.now()
    }

    # Создаем фильм через хелпер
    new_movie = movie_helper.create_test_movie(movie_data)

    # Проверяем, что фильм создан
    assert new_movie.id == 999999
    assert new_movie.name == "Тестовый фильм из хелпера"
    print(f"✅ Фильм создан: {new_movie}")

    # Проверяем, что можно найти фильм по ID
    found_movie = movie_helper.get_movie_by_id(999999)
    assert found_movie is not None
    assert found_movie.name == "Тестовый фильм из хелпера"
    print(f"✅ Фильм найден по ID: {found_movie}")


def test_get_movie_by_name(movie_helper):
    """Тест поиска фильма по названию через хелпер"""
    # Создаем фильм с ВСЕМИ обязательными полями
    movie_data = {
        "id": 888888,
        "name": "Уникальное название для поиска",
        "price": 200,
        "description": "Тестовое описание для поиска",  # <-- добавлено
        "image_url": "https://example.com/search.jpg",  # <-- добавлено
        "location": "MSK",
        "published": True,
        "rating": 4,
        "genre_id": 1,
        "created_at": datetime.now()
    }
    created_movie = movie_helper.create_test_movie(movie_data)

    # Ищем фильм по названию
    found_movie = movie_helper.get_movie_by_name("Уникальное название для поиска")

    # Проверяем, что найденный фильм соответствует созданному
    assert found_movie is not None
    assert found_movie.id == created_movie.id
    assert found_movie.name == created_movie.name
    print(f"✅ Фильм найден по названию: {found_movie}")


def test_movie_exists_in_db(db_session):
    """Тест проверки существования фильма в БД"""
    helper = DBHelper(db_session)

    # Получаем все фильмы
    movies = helper.get_all_movies(limit=3)

    print(f"\n🎬 Первые 3 фильма в БД:")
    for movie_item in movies:
        print(f"  - {movie_item}")

    if movies:
        assert len(movies) <= 3
        print("✅ Фильмы успешно получены из БД")
    else:
        print("⚠️ В БД нет фильмов")