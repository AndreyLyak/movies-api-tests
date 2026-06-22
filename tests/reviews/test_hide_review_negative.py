# обновленный tests/reviews/test_hide_review_negative.py
import pytest
import allure
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


@allure.epic("Reviews")
@allure.feature("Скрытие отзывов")
@allure.story("Негативные сценарии - авторизация")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_hide_review_no_auth(api_manager, movie_payload):
    """Попытка скрыть отзыв без авторизации"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Test review")
        assert review_response.status_code == 201

        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PATCH запрос без токена авторизации"):
        resp = requests.patch(
            f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews/hide/{user_id}"
        )

    with allure.step("Проверка статус-кода 401 или 403"):
        assert resp.status_code in [401, 403], f"Ожидался 401 или 403, получен {resp.status_code}"
        allure.attach(str(resp.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Скрытие отзывов")
@allure.story("Негативные сценарии - несуществующий фильм")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_hide_review_not_found(api_manager):
    """Попытка скрыть отзыв у несуществующего фильма"""

    with allure.step("PATCH запрос с несуществующим movie_id"):
        resp = api_manager.reviews_api.hide_review(999999, "some-user-id", expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert resp.status_code == 404, f"Ожидался 404, получен {resp.status_code}"
        allure.attach(str(resp.json()), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Reviews")
@allure.feature("Скрытие отзывов")
@allure.story("Негативные сценарии - невалидный user_id")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_hide_review_invalid_user_id(api_manager, movie_payload):
    """Попытка скрыть отзыв с невалидным user_id"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PATCH запрос с невалидным user_id"):
        resp = api_manager.reviews_api.hide_review(movie_id, "invalid-id", expected_status=404)

    with allure.step("Проверка статус-кода (400 или 404)"):
        assert resp.status_code in [400, 404], f"Ожидался 400 или 404, получен {resp.status_code}"
        allure.attach(str(resp.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Скрытие отзывов")
@allure.story("Негативные сценарии - повторное скрытие")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_hide_review_already_hidden(api_manager, movie_payload):
    """Попытка скрыть уже скрытый отзыв"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Test review")
        assert review_response.status_code == 201

        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Первое скрытие отзыва (ожидаем 200)"):
        first_hide = api_manager.reviews_api.hide_review(movie_id, user_id)
        assert first_hide.status_code == 200, f"Ожидался 200, получен {first_hide.status_code}"
        allure.attach(str(first_hide.json()), name="First Hide Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Второе скрытие отзыва"):
        second_hide = api_manager.reviews_api.hide_review(movie_id, user_id)

    with allure.step("Проверка статус-кода (200, 400 или 409)"):
        assert second_hide.status_code in [200, 400,
                                           409], f"Ожидался 200, 400 или 409, получен {second_hide.status_code}"
        allure.attach(str(second_hide.json()), name="Second Hide Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)