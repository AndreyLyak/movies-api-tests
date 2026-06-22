# исправленный tests/movies/test_negative_create_movie.py
import pytest
import allure
import requests
import time
from constants import BASE_URL, MOVIES_ENDPOINT


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_create_movie_invalid_price(api_manager, movie_payload):
    """Попытка создать фильм с отрицательной ценой (API может принять)"""
    with allure.step("Подготовка данных с отрицательной ценой"):
        payload = movie_payload(price=-100)
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Отправка запроса на создание фильма"):
        response = api_manager.movies_api.create_movie(payload, expected_status=201)

    with allure.step("Проверка, что фильм создался (API принимает отрицательную цену)"):
        assert response.status_code == 201, f"Ожидался 201, получен {response.status_code}"
        movie_id = response.json().get("id")
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление созданного фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200
        print(f"✅ Фильм {movie_id} удален")


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_create_movie_duplicate(api_manager, movie_payload):
    """Попытка создать два фильма с одинаковым именем"""
    # Используем уникальное имя с timestamp
    unique_name = f"Test Movie Duplicate {int(time.time())}"

    with allure.step(f"Подготовка данных с фиксированным именем: {unique_name}"):
        payload = movie_payload(name=unique_name)
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание первого фильма (ожидаем 201)"):
        first_response = api_manager.movies_api.create_movie(payload, expected_status=201)
        assert first_response.status_code == 201, f"Ожидался 201, получен {first_response.status_code}"
        movie_id = first_response.json().get("id")
        allure.attach(str(movie_id), name="First Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Попытка создать дубликат фильма (ожидаем 409)"):
        second_response = api_manager.movies_api.create_movie(payload, expected_status=409)

    with allure.step("Проверка статус-кода 409 (Conflict)"):
        assert second_response.status_code == 409, f"Ожидался 409, получен {second_response.status_code}"
        allure.attach(str(second_response.json()), name="Error Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление созданного фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200
        print(f"✅ Фильм {movie_id} удален")


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