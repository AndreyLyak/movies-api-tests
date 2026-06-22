# tests/movies/test_negative_patch_movies.py
import pytest
import allure
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


@allure.epic("Movies")
@allure.feature("Обновление фильмов (PATCH)")
@allure.story("Негативные сценарии - авторизация")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_patch_without_auth(api_manager, movie_payload):
    """Попытка обновить фильм без авторизации"""
    with allure.step("Создание фильма через API"):
        response = api_manager.movies_api.create_movie(movie_payload())
        assert response.status_code == 201
        movie_id = response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PATCH запрос без токена авторизации"):
        url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}"
        patch_response = requests.patch(
            url,
            json={"name": "Updated without auth"}
        )

    with allure.step("Проверка статус-кода 401 или 403"):
        assert patch_response.status_code in [401, 403], f"Ожидался 401 или 403, получен {patch_response.status_code}"
        allure.attach(str(patch_response.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма через API"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200
        print(f"✅ Фильм {movie_id} удален")


@allure.epic("Movies")
@allure.feature("Обновление фильмов (PATCH)")
@allure.story("Негативные сценарии - несуществующий фильм")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_patch_nonexistent_movie(api_manager):
    """Попытка обновить несуществующий фильм"""
    nonexistent_id = 99999999

    with allure.step(f"PATCH запрос с несуществующим ID: {nonexistent_id}"):
        response = api_manager.movies_api.update_movie(nonexistent_id, {"name": "Updated"}, expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Movies")
@allure.feature("Обновление фильмов (PATCH)")
@allure.story("Негативные сценарии - некорректный ID")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_patch_invalid_id(api_manager):
    """Попытка обновить фильм с некорректным ID (строка)"""
    invalid_id = "abc"

    with allure.step(f"PATCH запрос с некорректным ID: {invalid_id}"):
        response = api_manager.movies_api.update_movie(invalid_id, {"name": "Updated"}, expected_status=404)

    with allure.step("Проверка статус-кода 400 или 404"):
        assert response.status_code in [400, 404], f"Ожидался 400 или 404, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Movies")
@allure.feature("Обновление фильмов (PATCH)")
@allure.story("Негативные сценарии - невалидные данные")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_patch_invalid_data(api_manager, movie_payload):
    """Попытка обновить фильм с отрицательной ценой (ожидаем 400)"""
    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PATCH запрос с отрицательной ценой (ожидаем 400)"):
        response = api_manager.movies_api.update_movie(movie_id, {"price": -100}, expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка сообщения об ошибке"):
        data = response.json()
        assert "message" in data, "Ответ должен содержать сообщение об ошибке"
        allure.attach(str(data), name="Error Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление фильма через API"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200
        print(f"✅ Фильм {movie_id} удален")


@allure.epic("Movies")
@allure.feature("Обновление фильмов (PATCH)")
@allure.story("Негативные сценарии - пустое тело")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_patch_empty_body(api_manager, movie_payload):
    """Попытка обновить фильм с пустым телом запроса"""
    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PATCH запрос с пустым телом"):
        response = api_manager.movies_api.update_movie(movie_id, {})

    with allure.step("Проверка статус-кода (200 или 400)"):
        # API может принять пустой запрос (ничего не менять) или отклонить
        assert response.status_code in [200, 400], f"Ожидался 200 или 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление фильма через API"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200
        print(f"✅ Фильм {movie_id} удален")