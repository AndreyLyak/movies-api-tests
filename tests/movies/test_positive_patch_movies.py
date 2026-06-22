# tests/movies/test_positive_patch_movies.py
import pytest
import allure
import uuid


@allure.epic("Movies")
@allure.feature("Обновление фильмов (PATCH)")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_update_movie(api_manager, movie_payload):
    """Позитивный тест: полное обновление фильма"""

    with allure.step("Подготовка данных для создания фильма"):
        create_payload = movie_payload()
        allure.attach(str(create_payload), name="Create Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(create_payload)
        assert create_response.status_code == 201, f"Ожидался 201, получен {create_response.status_code}"
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Подготовка данных для обновления"):
        unique_name = f"Updated Movie {uuid.uuid4()}"
        update_data = {
            "name": unique_name,
            "description": "Updated description",
            "price": 200,
            "location": "MSK",
            "imageUrl": "https://new-image.url",
            "published": False,
            "genreId": 1
        }
        allure.attach(str(update_data), name="Update Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Отправка PATCH-запроса на обновление фильма"):
        update_response = api_manager.movies_api.update_movie(movie_id, update_data)
        assert update_response.status_code == 200, f"Ожидался 200, получен {update_response.status_code}"

    with allure.step("Получение данных обновленного фильма"):
        data = update_response.json()
        allure.attach(str(data), name="Updated Movie Data", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка ID"):
        assert data["id"] == movie_id, f"ID не совпадает: ожидался {movie_id}, получен {data['id']}"

    with allure.step("Проверка обновленных полей"):
        assert data["name"] == update_data["name"], "Имя не совпадает"
        assert data["description"] == update_data["description"], "Описание не совпадает"
        assert data["price"] == update_data["price"], "Цена не совпадает"
        assert data["location"] == update_data["location"], "Локация не совпадает"
        assert data["imageUrl"] == update_data["imageUrl"], "imageUrl не совпадает"
        assert data["published"] == update_data["published"], "Статус published не совпадает"
        assert data["genreId"] == update_data["genreId"], "genreId не совпадает"

    with allure.step("Проверка, что обновленный фильм существует (GET)"):
        get_response = api_manager.movies_api.get_movie(movie_id)
        assert get_response.status_code == 200, f"Ожидался 200, получен {get_response.status_code}"
        get_data = get_response.json()
        assert get_data["name"] == update_data["name"], "Имя не совпадает при GET-запросе"

    with allure.step("Очистка: удаление созданного фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
        print(f"✅ Фильм {movie_id} удален")