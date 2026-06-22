# исправленный tests/movies/test_positive_delete_movie.py
import pytest
import allure
import uuid


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_positive_delete_movie(api_manager, movie_payload):
    """Позитивный тест: удаление фильма"""

    with allure.step("Подготовка данных с уникальным именем"):
        # Используем уникальное имя, чтобы избежать конфликтов
        unique_name = f"Delete Test Movie {uuid.uuid4()}"
        payload = movie_payload(name=unique_name)
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(payload)
        assert create_response.status_code == 201, f"Ожидался 201, получен {create_response.status_code}"
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что фильм существует (GET 200)"):
        get_response = api_manager.movies_api.get_movie(movie_id)
        assert get_response.status_code == 200, f"Ожидался 200, получен {get_response.status_code}"
        allure.attach(str(get_response.json()), name="Movie Data", attachment_type=allure.attachment_type.JSON)

    with allure.step("Удаление фильма (ожидаем 200)"):
        delete_response = api_manager.movies_api.delete_movie(movie_id)
        assert delete_response.status_code == 200, f"Ожидался 200, получен {delete_response.status_code}"
        allure.attach(str(delete_response.text), name="Delete Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что фильм удален (GET 404)"):
        get_after_delete = api_manager.movies_api.get_movie(movie_id, expected_status=404)
        assert get_after_delete.status_code == 404, f"Ожидался 404, получен {get_after_delete.status_code}"
        allure.attach(str(get_after_delete.json()), name="Get After Delete",
                      attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка сообщения об ошибке после удаления"):
        error_data = get_after_delete.json()
        assert "message" in error_data or "error" in error_data, "Ответ должен содержать сообщение об ошибке"

    print(f"✅ Фильм {movie_id} успешно удален")