# tests/reviews/test_review_show_negative.py
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
@allure.feature("Показ отзывов")
@allure.story("Негативные сценарии - авторизация")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_show_review_without_auth(api_manager, movie_payload):
    """Попытка показать отзыв без токена авторизации"""

    with allure.step("Создание фильма через API"):
        movie_resp = api_manager.movies_api.create_movie(movie_payload())
        assert movie_resp.status_code in [200, 201]
        movie_id = movie_resp.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_resp = api_manager.reviews_api.create_review(movie_id, rating=5, text="test")
        assert review_resp.status_code in [200, 201]

        review_data = review_resp.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data["userId"]
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id, user_id)
        assert review_before is not None, "Отзыв не найден в БД!"

    with allure.step("PATCH запрос без токена авторизации"):
        resp = requests.patch(
            f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews/show/{user_id}"
        )

    with allure.step("Проверка статус-кода 401"):
        assert resp.status_code == 401, f"Ожидался 401, получен {resp.status_code}"
        allure.attach(str(resp.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв остался в БД (не был показан без авторизации)"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is not None, "Отзыв исчез из БД!"
        allure.attach("Отзыв остался в БД", name="DB After", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Показ отзывов")
@allure.story("Негативные сценарии - несуществующий фильм")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_show_review_nonexistent_movie(api_manager):
    """Попытка показать отзыв у несуществующего фильма"""

    with allure.step("PATCH запрос с несуществующим movie_id"):
        resp = api_manager.reviews_api.show_review(999999, "some-user-id", expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert resp.status_code == 404, f"Ожидался 404, получен {resp.status_code}"
        allure.attach(str(resp.json()), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Reviews")
@allure.feature("Показ отзывов")
@allure.story("Негативные сценарии - несуществующий пользователь")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_show_review_nonexistent_user(api_manager, movie_payload):
    """Попытка показать отзыв с несуществующим user_id"""

    with allure.step("Создание фильма через API"):
        movie_resp = api_manager.movies_api.create_movie(movie_payload())
        assert movie_resp.status_code in [200, 201]
        movie_id = movie_resp.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_resp = api_manager.reviews_api.create_review(movie_id, rating=5, text="test")
        assert review_resp.status_code in [200, 201]
        review_data = review_resp.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        actual_user_id = review_data["userId"]
        allure.attach(str(actual_user_id), name="Actual User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id, actual_user_id)
        assert review_before is not None, "Отзыв не найден в БД!"

    with allure.step("PATCH запрос с несуществующим user_id"):
        resp = api_manager.reviews_api.show_review(movie_id, "fake-user-id", expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert resp.status_code == 404, f"Ожидался 404, получен {resp.status_code}"
        allure.attach(str(resp.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыв остался в БД (не был показан с несуществующим user_id)"):
        review_after = get_review_from_db(movie_id, actual_user_id)
        assert review_after is not None, "Отзыв исчез из БД!"
        allure.attach("Отзыв остался в БД", name="DB After", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Показ отзывов")
@allure.story("Негативные сценарии - невалидный user_id")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_show_review_invalid_user_id(api_manager, movie_payload):
    """Попытка показать отзыв с невалидным user_id (спецсимволы)"""

    with allure.step("Создание фильма через API"):
        movie_resp = api_manager.movies_api.create_movie(movie_payload())
        assert movie_resp.status_code in [200, 201]
        movie_id = movie_resp.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_resp = api_manager.reviews_api.create_review(movie_id, rating=5, text="test")
        assert review_resp.status_code in [200, 201]
        review_data = review_resp.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        actual_user_id = review_data["userId"]
        allure.attach(str(actual_user_id), name="Actual User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id, actual_user_id)
        assert review_before is not None, "Отзыв не найден в БД!"

    with allure.step("PATCH запрос с невалидным user_id '!!!'"):
        resp = api_manager.reviews_api.show_review(movie_id, "!!!", expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert resp.status_code == 404, f"Ожидался 404, получен {resp.status_code}"
        allure.attach(str(resp.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв остался в БД (не был показан с невалидным user_id)"):
        review_after = get_review_from_db(movie_id, actual_user_id)
        assert review_after is not None, "Отзыв исчез из БД!"
        allure.attach("Отзыв остался в БД", name="DB After", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)