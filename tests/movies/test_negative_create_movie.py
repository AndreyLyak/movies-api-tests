# tests/movies/test_negative_create_movie.py
import pytest
import allure
import requests
import time
from constants import BASE_URL, MOVIES_ENDPOINT
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


def check_movie_not_exists_in_db(movie_id: int) -> bool:
    """Проверяет, что фильм НЕ существует в БД."""
    session = SessionLocal()
    try:
        movie = session.query(MovieDBModel).filter_by(id=movie_id).first()
        return movie is None
    finally:
        session.close()


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_create_movie_invalid_price(api_manager, movie_payload):
    """Попытка создать фильм с отрицательной ценой (ожидаем 400)"""
    with allure.step("Подготовка данных с отрицательной ценой"):
        payload = movie_payload(price=-100)
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Отправка запроса на создание фильма (ожидаем 400)"):
        response = api_manager.movies_api.create_movie(payload, expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Error Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка сообщения об ошибке"):
        error_data = response.json()
        assert "price" in str(error_data).lower() or "больше 0" in str(error_data), "Ошибка должна быть связана с ценой"


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_create_movie_duplicate(api_manager, movie_payload):
    """Попытка создать два фильма с одинаковым именем"""
    unique_name = f"Test Movie Duplicate {int(time.time())}"

    with allure.step(f"Подготовка данных с фиксированным именем: {unique_name}"):
        payload = movie_payload(name=unique_name)
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание первого фильма (ожидаем 201)"):
        first_response = api_manager.movies_api.create_movie(payload, expected_status=201)
        assert first_response.status_code == 201, f"Ожидался 201, получен {first_response.status_code}"
        movie_id = first_response.json().get("id")
        allure.attach(str(movie_id), name="First Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что первый фильм появился в БД"):
        assert check_movie_exists_in_db(movie_id), f"Первый фильм с ID {movie_id} не найден в БД!"

    with allure.step("Попытка создать дубликат фильма (ожидаем 409)"):
        second_response = api_manager.movies_api.create_movie(payload, expected_status=409)

    with allure.step("Проверка статус-кода 409 (Conflict)"):
        assert second_response.status_code == 409, f"Ожидался 409, получен {second_response.status_code}"
        allure.attach(str(second_response.json()), name="Error Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление созданного фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200
        allure.attach(f"Фильм {movie_id} удален", name="Cleanup", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_create_movie_empty_name(api_manager, movie_payload):
    """Попытка создать фильм с пустым именем"""
    with allure.step("Подготовка данных с пустым именем"):
        payload = movie_payload(name="")
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Отправка запроса на создание фильма (ожидаем 400)"):
        response = api_manager.movies_api.create_movie(payload, expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Error Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что фильм НЕ создался в БД"):
        # ID не существует, так как фильм не создался
        assert "id" not in response.json(), "Фильм создался, хотя не должен был!"


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_create_movie_missing_required_field(api_manager, movie_payload):
    """Попытка создать фильм без обязательного поля (без name)"""
    with allure.step("Подготовка данных без поля name"):
        payload = movie_payload()
        del payload["name"]
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Отправка запроса на создание фильма (ожидаем 400)"):
        response = api_manager.movies_api.create_movie(payload, expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Error Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что фильм НЕ создался в БД"):
        # ID не существует, так как фильм не создался
        assert "id" not in response.json(), "Фильм создался, хотя не должен был!"


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_create_movie_invalid_genre(api_manager, movie_payload):
    """Попытка создать фильм с несуществующим жанром"""
    with allure.step("Подготовка данных с несуществующим genreId=999"):
        payload = movie_payload(genreId=999)
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Отправка запроса на создание фильма (ожидаем 400)"):
        response = api_manager.movies_api.create_movie(payload, expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Error Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что фильм НЕ создался в БД"):
        assert "id" not in response.json(), "Фильм создался, хотя не должен был!"


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_create_movie_without_auth(movie_payload):
    """Попытка создать фильм без авторизации"""
    with allure.step("Подготовка данных для создания фильма"):
        payload = movie_payload()
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Отправка запроса без токена авторизации (ожидаем 401)"):
        response = requests.post(
            f"{BASE_URL}{MOVIES_ENDPOINT}",
            json=payload
        )

    with allure.step("Проверка статус-кода 401 (Unauthorized)"):
        assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"
        allure.attach(str(response.json()), name="Error Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что фильм НЕ создался в БД"):
        # При 401 ответе ID не будет
        assert "id" not in response.json(), "Фильм создался без авторизации!"
