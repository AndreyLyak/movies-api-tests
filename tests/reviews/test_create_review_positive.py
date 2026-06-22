# обновленный tests/reviews/test_create_review_positive.py
import pytest
import allure


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_update_review(api_manager, movie_payload):
    """Позитивный тест: создание и обновление отзыва"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201, f"Ожидался 201, получен {create_response.status_code}"
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review text")
        assert review_response.status_code == 201, f"Ожидался 201, получен {review_response.status_code}"

        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]

        user_id = review_data.get("userId")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(review_data), name="Created Review", attachment_type=allure.attachment_type.JSON)

    with allure.step("Обновление отзыва (изменение рейтинга и текста)"):
        update_payload = {
            "rating": 4,
            "text": "updated text"
        }
        allure.attach(str(update_payload), name="Update Payload", attachment_type=allure.attachment_type.JSON)

        update_resp = api_manager.reviews_api.update_review(movie_id, rating=4, text="updated text")
        assert update_resp.status_code == 200, f"Ожидался 200, получен {update_resp.status_code}"

    with allure.step("Получение данных обновленного отзыва"):
        result = update_resp.json()
        allure.attach(str(result), name="Updated Review Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка структуры ответа"):
        # API может вернуть объект или список
        reviews = result if isinstance(result, list) else [result]
        assert len(reviews) > 0, "Ответ не содержит отзывов"

    with allure.step("Проверка обновленных данных"):
        found = False
        for review in reviews:
            if review.get("text") == update_payload["text"]:
                found = True
                assert review.get("rating") == update_payload[
                    "rating"], f"Рейтинг не совпадает: ожидался {update_payload['rating']}, получен {review.get('rating')}"
                assert "createdAt" in review, "Поле 'createdAt' отсутствует"
                assert "movieId" in review, "Поле 'movieId' отсутствует"
                assert review.get(
                    "userId") == user_id, f"userId не совпадает: ожидался {user_id}, получен {review.get('userId')}"

                allure.attach("Все проверки пройдены", name="Success", attachment_type=allure.attachment_type.TEXT)

        assert found, f"Обновленный отзыв не найден в ответе: {result}"

    with allure.step("Очистка: удаление фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
        print(f"✅ Фильм {movie_id} удален")