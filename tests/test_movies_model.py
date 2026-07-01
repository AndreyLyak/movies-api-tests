# tests/test_movies_model.py
import sys
import os
from datetime import datetime
from sqlalchemy import text  # <-- добавляем импорт

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_requester.db_client import SessionLocal
from db_requester.movies import MovieDBModel


def test_movies_table_exists():
    """Проверяем, что таблица movies существует в БД"""
    session = SessionLocal()
    try:
        # Проверяем, есть ли таблица movies
        result = session.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'movies')")
        ).scalar()

        assert result is True, "Таблица movies не найдена в БД!"
        print("✅ Таблица movies существует")

        # Проверяем колонки
        columns = session.execute(
            text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'movies'
                ORDER BY ordinal_position
            """)
        ).fetchall()

        print("\n📊 Структура таблицы movies:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")

    finally:
        session.close()


def test_movie_model_creation():
    """Проверяем создание объекта модели"""
    # Создаем объект модели
    movie = MovieDBModel(
        id=999,  # временный ID для теста
        name="Тестовый фильм",
        price=100,
        description="Тестовое описание",
        image_url="https://example.com/test.jpg",
        location="Test Location",
        published=True,
        rating=5,
        genre_id=1,
        created_at=datetime.now()
    )

    # Проверяем, что объект создался
    assert movie.id == 999
    assert movie.name == "Тестовый фильм"
    assert movie.price == 100
    assert movie.published is True
    print("✅ Объект MovieDBModel создан успешно")

    # Проверяем метод to_dict()
    movie_dict = movie.to_dict()
    assert movie_dict['id'] == 999
    assert movie_dict['name'] == "Тестовый фильм"
    assert 'created_at' in movie_dict
    print("✅ Метод to_dict() работает")

    # Проверяем метод __repr__()
    print(f"✅ __repr__(): {movie}")


def test_query_movies():
    """Проверяем запрос к таблице movies"""
    session = SessionLocal()
    try:
        # Получаем первые 5 фильмов
        movies = session.query(MovieDBModel).limit(5).all()

        print(f"\n🎬 Найдено фильмов (первые 5): {len(movies)}")
        for movie in movies:
            print(f"  - {movie}")  # Используем __repr__

        # Если есть фильмы, проверяем, что они правильного типа
        if movies:
            assert isinstance(movies[0], MovieDBModel)
            print("✅ Запрос к таблице movies работает")
        else:
            print("⚠️ В таблице movies нет данных")

    finally:
        session.close()


def test_get_movie_by_id():
    """Проверяем получение фильма по ID"""
    session = SessionLocal()
    try:
        # Проверяем, есть ли фильмы с id
        movie = session.query(MovieDBModel).first()

        if movie:
            # Получаем фильм по id
            found_movie = session.query(MovieDBModel).filter_by(id=movie.id).first()
            assert found_movie is not None
            assert found_movie.id == movie.id
            print(f"✅ Найден фильм по ID {movie.id}: {found_movie}")
        else:
            print("⚠️ В таблице movies нет данных для проверки")

    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Тестирование модели MovieDBModel")
    print("=" * 60)

    try:
        # Проверка 1: существует ли таблица
        test_movies_table_exists()
        print()

        # Проверка 2: создание объекта
        test_movie_model_creation()
        print()

        # Проверка 3: запрос к БД
        test_query_movies()
        print()

        # Проверка 4: поиск по ID
        test_get_movie_by_id()

        print("\n" + "=" * 60)
        print("✅ Все тесты пройдены успешно!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Тест не пройден: {e}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")