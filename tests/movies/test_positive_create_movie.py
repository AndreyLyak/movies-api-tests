# tests/movies/test_positive_create_movie.py
import pytest
import allure
from db_requester.db_client import SessionLocal
from db_requester.movies import MovieDBModel


def check_movie_exists_in_db(movie_id: int) -> bool:
    """Проверяет, существует ли фильм в БД."""
    session = SessionLocal()
    try:
        movie = session.query(MovieDBModel).filter_by(id=movie_id).first()
        return movie is not None
    finally:
        session.close()


def get_movie_from_db(movie_id: int):
    """Получает фильм из БД по ID."""
    session = SessionLocal()
    try:
        return session.query(MovieDBModel).filter_by(id=movie_id).first()
    finally:
        session.close()


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_create_movie(api_manager, movie_payload):
    """Позитивный тест: создание фильма с валидными данными"""

    with allure.step("Подготовка данных для создания фильма"):
        payload = movie_payload()
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание фильма через API"):
        response = api_manager.movies_api.create_movie(payload)
        assert response.status_code in [200, 201], f"Ожидался 200 или 201, получен {response.status_code}"

    with allure.step("Получение данных созданного фильма"):
        data = response.json()
        allure.attach(str(data), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка наличия ID"):
        assert "id" in data, "Ответ не содержит ID"
        movie_id = data["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка названия фильма"):
        assert data["name"] == payload["name"], f"Ожидалось имя {payload['name']}, получено {data['name']}"

    with allure.step("Проверка дополнительных полей"):
        assert data["price"] == payload["price"], "Цена не совпадает"
        assert data["location"] == payload["location"], "Локация не совпадает"
        assert data["published"] == payload["published"], "Статус published не совпадает"

    with allure.step("Проверка, что фильм появился в БД"):
        assert check_movie_exists_in_db(movie_id), f"Фильм с ID {movie_id} не найден в БД!"
        movie_from_db = get_movie_from_db(movie_id)
        assert movie_from_db.name == payload["name"], f"Имя в БД не совпадает: {movie_from_db.name} != {payload['name']}"
        assert movie_from_db.price == payload["price"], f"Цена в БД не совпадает: {movie_from_db.price} != {payload['price']}"
        allure.attach("Фильм успешно создан в БД", name="DB Check", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление созданного фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
        allure.attach(f"Фильм {movie_id} удален", name="Cleanup", attachment_type=allure.attachment_type.TEXT)
