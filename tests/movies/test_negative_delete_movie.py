#исправленный tests/movies/test_negative_delete_movie.py
import pytest
import allure
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_delete_without_auth(api_manager, movie_payload):
    """Попытка удалить фильм без авторизации"""
    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что фильм существует"):
        get_response = api_manager.movies_api.get_movie(movie_id)
        assert get_response.status_code == 200

    with allure.step("DELETE запрос без токена авторизации"):
        url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}"
        delete_response = requests.delete(url)

    with allure.step("Проверка статус-кода 401 или 403"):
        assert delete_response.status_code in [401, 403], f"Ожидался 401 или 403, получен {delete_response.status_code}"
        allure.attach(str(delete_response.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма через API"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200
        print(f"✅ Фильм {movie_id} удален")


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_delete_nonexistent_movie(api_manager):
    """Попытка удалить несуществующий фильм"""
    nonexistent_id = 999999999

    with allure.step(f"DELETE запрос с несуществующим ID: {nonexistent_id}"):
        response = api_manager.movies_api.delete_movie(nonexistent_id, expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_delete_invalid_id(api_manager):
    """Попытка удалить фильм с некорректным ID (строка)"""
    invalid_id = "abc"

    with allure.step(f"DELETE запрос с некорректным ID: {invalid_id}"):
        response = api_manager.movies_api.delete_movie(invalid_id, expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.story("Негативные сценарии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_double_delete_movie(api_manager, movie_payload):
    """Попытка удалить один фильм дважды"""
    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Первое удаление фильма (ожидаем 200)"):
        first_delete = api_manager.movies_api.delete_movie(movie_id)
        assert first_delete.status_code == 200, f"Ожидался 200, получен {first_delete.status_code}"

    with allure.step("Второе удаление фильма (ожидаем 404)"):
        second_delete = api_manager.movies_api.delete_movie(movie_id, expected_status=404)
        assert second_delete.status_code == 404, f"Ожидался 404, получен {second_delete.status_code}"
        allure.attach(str(second_delete.json()), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_delete_then_get_movie(api_manager, movie_payload):
    """Удаление фильма и проверка, что он исчез"""
    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что фильм существует (GET 200)"):
        get_response = api_manager.movies_api.get_movie(movie_id)
        assert get_response.status_code == 200, f"Ожидался 200, получен {get_response.status_code}"

    with allure.step("Удаление фильма (ожидаем 200)"):
        delete_response = api_manager.movies_api.delete_movie(movie_id)
        assert delete_response.status_code == 200, f"Ожидался 200, получен {delete_response.status_code}"

    with allure.step("Проверка, что фильм исчез (GET 404)"):
        get_after_delete = api_manager.movies_api.get_movie(movie_id, expected_status=404)
        assert get_after_delete.status_code == 404, f"Ожидался 404, получен {get_after_delete.status_code}"
        allure.attach(str(get_after_delete.json()), name="Response", attachment_type=allure.attachment_type.JSON)