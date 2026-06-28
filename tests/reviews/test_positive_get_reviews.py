# обновленный tests/reviews/test_positive_get_reviews.py
import pytest
import allure
import uuid


@allure.epic("Reviews")
@allure.feature("Получение отзывов")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_get_reviews_by_movie_id(api_manager, movie_payload):
    """Позитивный тест: получение отзывов по ID фильма"""

    with allure.step("Подготовка данных для фильма с уникальным именем"):
        unique_name = f"Get Reviews Test {uuid.uuid4()}"
        payload = movie_payload(name=unique_name)
        allure.attach(str(payload), name="Create Movie Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(payload)
        assert create_response.status_code == 201, f"Ожидался 201, получен {create_response.status_code}"
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_payload = {
            "rating": 5,
            "text": f"Test review {uuid.uuid4()}"
        }
        allure.attach(str(review_payload), name="Review Payload", attachment_type=allure.attachment_type.JSON)

        create_review_resp = api_manager.reviews_api.create_review(movie_id, **review_payload)
        assert create_review_resp.status_code in [200,
                                                  201], f"Ожидался 200 или 201, получен {create_review_resp.status_code}"
        allure.attach(str(create_review_resp.json()), name="Created Review",
                      attachment_type=allure.attachment_type.JSON)

    with allure.step("Получение отзывов для фильма"):
        response = api_manager.reviews_api.get_reviews(movie_id)
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"

    with allure.step("Проверка структуры ответа"):
        data = response.json()
        allure.attach(str(data), name="Reviews Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что ответ является списком"):
        assert isinstance(data, list), "Ответ должен быть списком"
        assert len(data) > 0, "Ожидаем хотя бы один отзыв после создания"

    with allure.step("Проверка структуры первого отзыва"):
        review = data[0]
        required_fields = ["userId", "rating", "text", "createdAt", "user"]
        for field in required_fields:
            assert field in review, f"Поле '{field}' отсутствует в отзыве"

        assert "fullName" in review["user"], "Поле 'fullName' отсутствует в объекте user"
        allure.attach("Структура отзыва корректна", name="Structure Check", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка данных созданного отзыва"):
        # Проверяем, что созданный отзыв есть в списке
        found = False
        for rev in data:
            if rev["text"] == review_payload["text"]:
                found = True
                assert rev["rating"] == review_payload[
                    "rating"], f"Рейтинг не совпадает: ожидался {review_payload['rating']}, получен {rev['rating']}"
                allure.attach(f"Найден отзыв: {rev}", name="Found Review", attachment_type=allure.attachment_type.JSON)
                break

        assert found, f"Созданный отзыв с текстом '{review_payload['text']}' не найден в списке"

    with allure.step("Очистка: удаление фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
        allure.attach(f"Фильм {movie_id} удален", name="Cleanup", attachment_type=allure.attachment_type.TEXT)
