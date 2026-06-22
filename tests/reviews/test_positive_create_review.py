#обновленный tests/reviews/test_positive_create_review.py
import pytest
import allure
import uuid


@allure.epic("Reviews")
@allure.feature("Создание отзывов")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_create_review(api_manager, movie_payload):
    """Позитивный тест: создание отзыва для фильма"""

    with allure.step("Подготовка данных для фильма с уникальным именем"):
        unique_name = f"Review Test Movie {uuid.uuid4()}"
        payload = movie_payload(name=unique_name)
        allure.attach(str(payload), name="Create Movie Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(payload)
        assert create_response.status_code in [200, 201], f"Ожидался 200 или 201, получен {create_response.status_code}"
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Подготовка данных для отзыва"):
        review_data = {
            "rating": 4,
            "text": "Хорошее кино"
        }
        allure.attach(str(review_data), name="Review Data", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание отзыва через API"):
        response = api_manager.reviews_api.create_review(
            movie_id,
            rating=review_data["rating"],
            text=review_data["text"]
        )

    with allure.step("Проверка статус-кода 200 или 201"):
        assert response.status_code in [200, 201], f"Ожидался 200 или 201, получен {response.status_code}"

    with allure.step("Получение данных созданного отзыва"):
        data = response.json()
        allure.attach(str(data), name="Review Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка структуры ответа"):
        assert isinstance(data, dict), "Ответ должен быть объектом"

    with allure.step("Проверка данных отзыва"):
        assert data["rating"] == review_data[
            "rating"], f"Рейтинг не совпадает: ожидался {review_data['rating']}, получен {data['rating']}"
        assert data["text"] == review_data[
            "text"], f"Текст не совпадает: ожидался {review_data['text']}, получен {data['text']}"

    with allure.step("Проверка наличия обязательных полей"):
        assert "userId" in data, "Поле 'userId' отсутствует"
        assert "createdAt" in data, "Поле 'createdAt' отсутствует"
        assert "user" in data, "Поле 'user' отсутствует"
        assert "fullName" in data["user"], "Поле 'fullName' отсутствует в объекте user"
        allure.attach("Все обязательные поля присутствуют", name="Success", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
        print(f"✅ Фильм {movie_id} удален")