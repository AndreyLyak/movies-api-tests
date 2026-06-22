#обновленный tests/reviews/test_show_review_positive.py
import pytest
import allure
import uuid


@allure.epic("Reviews")
@allure.feature("Показ отзывов")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_show_review(api_manager, movie_payload):
    """Позитивный тест: скрытие и показ отзыва"""

    with allure.step("Подготовка данных для фильма с уникальным именем"):
        unique_name = f"Show Review Test {uuid.uuid4()}"
        payload = movie_payload(name=unique_name)
        allure.attach(str(payload), name="Create Movie Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание фильма через API"):
        movie_resp = api_manager.movies_api.create_movie(payload)
        assert movie_resp.status_code in [200, 201], f"Ожидался 200 или 201, получен {movie_resp.status_code}"
        movie_id = movie_resp.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_resp = api_manager.reviews_api.create_review(movie_id, rating=5, text=f"Test review {uuid.uuid4()}")
        assert review_resp.status_code in [200, 201], f"Ожидался 200 или 201, получен {review_resp.status_code}"

        review_data = review_resp.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data["userId"]
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(review_data), name="Created Review", attachment_type=allure.attachment_type.JSON)

    with allure.step("Скрытие отзыва"):
        hide_resp = api_manager.reviews_api.hide_review(movie_id, user_id)
        assert hide_resp.status_code == 200, f"Ожидался 200, получен {hide_resp.status_code}"
        allure.attach(str(hide_resp.json()), name="Hide Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Показ отзыва обратно"):
        show_resp = api_manager.reviews_api.show_review(movie_id, user_id)
        assert show_resp.status_code == 200, f"Ожидался 200, получен {show_resp.status_code}"

    with allure.step("Получение данных показанного отзыва"):
        data = show_resp.json()
        allure.attach(str(data), name="Show Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка данных отзыва"):
        assert data["userId"] == user_id, f"userId не совпадает: ожидался {user_id}, получен {data['userId']}"
        assert "rating" in data, "Поле 'rating' отсутствует"
        assert "text" in data, "Поле 'text' отсутствует"
        assert "createdAt" in data, "Поле 'createdAt' отсутствует"
        allure.attach("Все проверки пройдены", name="Success", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
        print(f"✅ Фильм {movie_id} удален")