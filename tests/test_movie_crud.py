# tests/test_movie_crud.py
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_movie_full_lifecycle(db_helper, api_manager, test_movie_data, created_test_movie):
    """
    Полный тест жизненного цикла фильма:
    1. Проверка: до создания фильма нет
    2. Создание через API
    3. Проверка: после создания фильм есть в БД
    4. Удаление через API
    5. Проверка: после удаления фильма нет в БД
    """

    # ========== ШАГ 1: Проверка ДО создания ==========
    print("\n📋 ШАГ 1: Проверка, что фильма нет в БД до создания")

    movie_id = test_movie_data["id"]

    # Проверяем, что фильма нет в БД (если есть - удаляем)
    if db_helper.movie_exists_by_id(movie_id):
        existing_movie = db_helper.get_movie_by_id(movie_id)
        db_helper.delete_movie(existing_movie)
        print(f"🧹 Очистка: удален существующий фильм {movie_id}")

    assert not db_helper.movie_exists_by_id(movie_id), f"Фильм с ID {movie_id} уже существует в БД!"
    print(f"✅ Фильма с ID {movie_id} нет в БД")

    # Сохраняем количество фильмов до создания
    count_before = db_helper.get_movie_count()
    print(f"📊 Количество фильмов до создания: {count_before}")

    # ========== ШАГ 2: Создание фильма через API ==========
    print("\n📋 ШАГ 2: Создание фильма через API")

    # Подготавливаем payload для API
    api_payload = {
        "name": test_movie_data["name"],
        "price": test_movie_data["price"],
        "description": test_movie_data["description"],
        "imageUrl": test_movie_data["image_url"],
        "location": test_movie_data["location"],
        "published": test_movie_data["published"],
        "genreId": test_movie_data["genre_id"]
    }

    # Создаем фильм через API
    response = api_manager.movies_api.create_movie(api_payload)

    # Проверяем, что API вернул успешный ответ
    assert response.status_code in [200, 201], f"Ошибка создания фильма: {response.status_code}"
    movie_data_from_api = response.json()

    # Получаем ID из ответа API
    actual_movie_id = movie_data_from_api.get("id")
    print(f"✅ Фильм создан через API с ID: {actual_movie_id}")

    # Если API вернул другой ID, обновляем
    if actual_movie_id and actual_movie_id != movie_id:
        print(f"⚠️ API создал фильм с ID {actual_movie_id} вместо {movie_id}")
        movie_id = actual_movie_id

    # ========== ШАГ 3: Проверка ПОСЛЕ создания ==========
    print("\n📋 ШАГ 3: Проверка, что фильм появился в БД")

    # Проверяем, что фильм появился в БД
    assert db_helper.movie_exists_by_id(movie_id), f"Фильм с ID {movie_id} не появился в БД после создания!"
    print(f"✅ Фильм с ID {movie_id} появился в БД")

    # Проверяем, что данные в БД совпадают с отправленными
    movie_in_db = db_helper.get_movie_by_id(movie_id)
    assert movie_in_db is not None
    assert movie_in_db.name == test_movie_data[
        "name"], f"Имя фильма не совпадает: {movie_in_db.name} != {test_movie_data['name']}"
    assert movie_in_db.price == test_movie_data[
        "price"], f"Цена фильма не совпадает: {movie_in_db.price} != {test_movie_data['price']}"
    assert movie_in_db.location == test_movie_data[
        "location"], f"Локация фильма не совпадает: {movie_in_db.location} != {test_movie_data['location']}"
    print(f"✅ Данные в БД совпадают с отправленными")

    # Проверяем, что количество фильмов увеличилось на 1
    count_after_create = db_helper.get_movie_count()
    assert count_after_create == count_before + 1, f"Количество фильмов не увеличилось: {count_before} -> {count_after_create}"
    print(f"📊 Количество фильмов после создания: {count_after_create}")

    # ========== ШАГ 4: Удаление фильма через API ==========
    print("\n📋 ШАГ 4: Удаление фильма через API")

    # Удаляем фильм через API
    delete_response = api_manager.movies_api.delete_movie(movie_id)
    assert delete_response.status_code in [200, 204], f"Ошибка удаления фильма: {delete_response.status_code}"
    print(f"✅ Фильм с ID {movie_id} удален через API")

    # ========== ШАГ 5: Проверка ПОСЛЕ удаления ==========
    print("\n📋 ШАГ 5: Проверка, что фильм удален из БД")

    # Проверяем, что фильм удален из БД
    assert not db_helper.movie_exists_by_id(movie_id), f"Фильм с ID {movie_id} остался в БД после удаления!"
    print(f"✅ Фильма с ID {movie_id} нет в БД")

    # Проверяем, что количество фильмов вернулось к исходному
    count_after_delete = db_helper.get_movie_count()
    assert count_after_delete == count_before, f"Количество фильмов не вернулось к исходному: {count_before} -> {count_after_delete}"
    print(f"📊 Количество фильмов после удаления: {count_after_delete}")

    print("\n" + "=" * 60)
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Жизненный цикл фильма работает корректно.")
    print("=" * 60)


def test_movie_creation_via_api(db_helper, api_manager):
    """
    Тест создания фильма через API с проверкой в БД
    """
    print("\n" + "=" * 60)
    print("🧪 Тест: Создание фильма через API")
    print("=" * 60)

    # Уникальные данные для теста
    test_name = f"API Фильм {datetime.now().timestamp()}"

    movie_payload = {
        "name": test_name,
        "price": 500,
        "description": "Создан через API тест",
        "imageUrl": "https://example.com/api_test.jpg",
        "location": "MSK",
        "published": True,
        "genreId": 1
    }

    # Проверка ДО: фильма нет в БД
    assert not db_helper.movie_exists_by_name(test_name), f"Фильм '{test_name}' уже существует в БД!"
    print("✅ До создания: фильма нет в БД")

    # Создание через API
    response = api_manager.movies_api.create_movie(movie_payload)
    assert response.status_code in [200, 201], f"Ошибка создания: {response.status_code}"
    movie_data = response.json()
    movie_id = movie_data.get("id")
    print(f"✅ Фильм создан через API с ID: {movie_id}")

    # Проверка ПОСЛЕ: фильм появился в БД
    assert db_helper.movie_exists_by_id(movie_id), f"Фильм с ID {movie_id} не появился в БД!"
    movie_in_db = db_helper.get_movie_by_id(movie_id)
    assert movie_in_db.name == test_name, f"Имя не совпадает: {movie_in_db.name} != {test_name}"
    print("✅ После создания: фильм появился в БД с правильными данными")

    # Очистка: удаляем тестовый фильм
    delete_response = api_manager.movies_api.delete_movie(movie_id)
    assert delete_response.status_code in [200, 204]

    # Проверка: фильм удален из БД
    assert not db_helper.movie_exists_by_id(movie_id), f"Фильм с ID {movie_id} остался в БД!"
    print("✅ После удаления: фильма нет в БД")

    print("\n✅ Тест пройден!")