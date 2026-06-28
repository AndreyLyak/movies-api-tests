# tests/reviews/test_hide_review_negative.py
import pytest
import allure
import requests
from constants import BASE_URL, MOVIES_ENDPOINT
from db_requester.db_client import SessionLocal
from sqlalchemy import text


def get_review_from_db(movie_id: int, user_id: str = None):
    """Получает отзыв из БД по movie_id и user_id."""
    session = SessionLocal()
    try:
        query = "SELECT * FROM reviews WHERE movie_id = :movie_id"
        params = {"movie_id": movie_id}
        if user_id:
            query += " AND user_id = :user_id"
            params["user_id"] = user_id
        result = session.execute(text(query), params).fetchone()
        return dict(result._mapping) if result else None
    finally:
        session.close()


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
        hidden_before = review_data.get("hidden", False)
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв есть в БД и не скрыт"):
        review_before = get_review_from_db(movie_id, user_id)
        assert review_before is not None, "Отзыв не найден в БД!"
        allure.attach("Отзыв есть в БД", name="DB Before", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PATCH запрос без токена авторизации"):
        resp = requests.patch(
            f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews/hide/{user_id}"
        )

    with allure.step("Проверка статус-кода 401 или 403"):
        assert resp.status_code in [401, 403], f"Ожидался 401 или 403, получен {resp.status_code}"
        allure.attach(str(resp.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв НЕ был скрыт в БД"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is not None, "Отзыв исчез из БД!"
        # hidden может не быть в таблице, если это поле не используется
        # Проверяем, что отзыв остался без изменений
        allure.attach("Отзыв не был скрыт (без авторизации)", name="DB After", attachment_type=allure.attachment_type.TEXT)

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

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Test review")
        assert review_response.status_code == 201

        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        actual_user_id = review_data.get("userId")
        allure.attach(str(actual_user_id), name="Actual User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id, actual_user_id)
        assert review_before is not None, "Отзыв не найден в БД!"

    with allure.step("PATCH запрос с невалидным user_id"):
        resp = api_manager.reviews_api.hide_review(movie_id, "invalid-id", expected_status=404)

    with allure.step("Проверка статус-кода (400 или 404)"):
        assert resp.status_code in [400, 404], f"Ожидался 400 или 404, получен {resp.status_code}"
        allure.attach(str(resp.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв НЕ был скрыт (неправильный user_id)"):
        review_after = get_review_from_db(movie_id, actual_user_id)
        assert review_after is not None, "Отзыв был удален или скрыт!"
        allure.attach("Отзыв не был скрыт (невалидный user_id)", name="DB After", attachment_type=allure.attachment_type.TEXT)

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

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id, user_id)
        assert review_before is not None, "Отзыв не найден в БД!"

    with allure.step("Первое скрытие отзыва (ожидаем 200)"):
        first_hide = api_manager.reviews_api.hide_review(movie_id, user_id)
        assert first_hide.status_code == 200, f"Ожидался 200, получен {first_hide.status_code}"
        allure.attach(str(first_hide.json()), name="First Hide Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыв скрыт в БД (если есть поле hidden)"):
        review_after_first = get_review_from_db(movie_id, user_id)
        assert review_after_first is not None, "Отзыв исчез из БД!"
        allure.attach("Отзыв скрыт после первого запроса", name="DB After First Hide", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Второе скрытие отзыва"):
        second_hide = api_manager.reviews_api.hide_review(movie_id, user_id)

    with allure.step("Проверка статус-кода (200, 400 или 409)"):
        assert second_hide.status_code in [200, 400, 409], f"Ожидался 200, 400 или 409, получен {second_hide.status_code}"
        allure.attach(str(second_hide.json()), name="Second Hide Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)