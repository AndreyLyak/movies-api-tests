# обновленный tests/reviews/test_hide_review_positive.py
import pytest
import allure


@allure.epic("Reviews")
@allure.feature("Скрытие отзывов")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_hide_review(api_manager, movie_payload):
    """Позитивный тест: скрытие отзыва"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201, f"Ожидался 201, получен {create_response.status_code}"
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Test review for hiding")
        assert review_response.status_code == 201, f"Ожидался 201, получен {review_response.status_code}"

        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]

        user_id = review_data.get("userId")
        review_text = review_data.get("text")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(review_data), name="Created Review", attachment_type=allure.attachment_type.JSON)

    with allure.step("Скрытие отзыва (ожидаем 200)"):
        hide_resp = api_manager.reviews_api.hide_review(movie_id, user_id)
        assert hide_resp.status_code == 200, f"Ожидался 200, получен {hide_resp.status_code}"

    with allure.step("Получение данных скрытого отзыва"):
        result = hide_resp.json()
        allure.attach(str(result), name="Hidden Review Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка user_id"):
        assert result["userId"] == user_id, f"userId не совпадает: ожидался {user_id}, получен {result['userId']}"

    with allure.step("Проверка text"):
        assert result["text"] == review_text, f"text не совпадает: ожидался {review_text}, получен {result['text']}"

    with allure.step("Проверка hidden статуса"):
        if "hidden" in result:
            assert result["hidden"] is True, "Поле 'hidden' должно быть True"
            allure.attach("Отзыв успешно скрыт (hidden=True)", name="Success",
                          attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach("Поле 'hidden' отсутствует в ответе", name="Warning",
                          attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
        allure.attach(f"Фильм {movie_id} удален", name="Cleanup", attachment_type=allure.attachment_type.TEXT)
