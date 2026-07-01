# tests/reviews/test_delete_review_negative.py
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
@allure.feature("Удаление отзывов")
@allure.story("Негативные сценарии - авторизация")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_delete_review_no_auth(api_manager, movie_payload):
    """Попытка удалить отзыв без авторизации"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201
        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        allure.attach(str(review_data), name="Review Data", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id, user_id)
        assert review_before is not None, "Отзыв не найден в БД!"

    with allure.step("DELETE запрос без токена авторизации"):
        resp = requests.delete(
            f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews"
        )

    with allure.step("Проверка статус-кода 401 или 403"):
        assert resp.status_code in [401, 403], f"Ожидался 401 или 403, получен {resp.status_code}"
        allure.attach(str(resp.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв остался в БД"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is not None, "Отзыв был удален без авторизации!"
        allure.attach("Отзыв остался в БД", name="DB After", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Удаление отзывов")
@allure.story("Негативные сценарии - несуществующий фильм")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_delete_review_not_found(api_manager):
    """Попытка удалить отзыв у несуществующего фильма"""

    with allure.step("DELETE запрос с несуществующим movie_id"):
        resp = api_manager.reviews_api.delete_review(999999, expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert resp.status_code == 404, f"Ожидался 404, получен {resp.status_code}"
        allure.attach(str(resp.json()), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Reviews")
@allure.feature("Удаление отзывов")
@allure.story("Негативные сценарии - отсутствует отзыв")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_delete_review_without_existing_review(api_manager, movie_payload):
    """Попытка удалить отзыв, которого не существует"""

    with allure.step("Создание фильма через API"):
        movie_resp = api_manager.movies_api.create_movie(movie_payload())
        movie_id = movie_resp.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыва нет в БД"):
        review_before = get_review_from_db(movie_id)
        assert review_before is None, "Отзыв уже существует в БД!"

    with allure.step("DELETE запрос без создания отзыва"):
        resp = api_manager.reviews_api.delete_review(movie_id, expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert resp.status_code == 404, f"Ожидался 404, получен {resp.status_code}"
        allure.attach(str(resp.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Удаление отзывов")
@allure.story("Негативные сценарии - невалидный ID")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_delete_review_invalid_movie_id(api_manager):
    """Попытка удалить отзыв с невалидным movie_id"""

    with allure.step("DELETE запрос с невалидным movie_id 'abc'"):
        resp = api_manager.reviews_api.delete_review("abc", expected_status=404)

    with allure.step("Проверка статус-кода (400 или 404)"):
        assert resp.status_code in [400, 404], f"Ожидался 400 или 404, получен {resp.status_code}"
        allure.attach(str(resp.text), name="Response", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Reviews")
@allure.feature("Удаление отзывов")
@allure.story("Негативные сценарии - повторное удаление")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_delete_review_double_delete(api_manager, movie_payload):
    """Попытка удалить отзыв дважды"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201

        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id, user_id)
        assert review_before is not None, "Отзыв не найден в БД!"

    with allure.step("Первое удаление отзыва (ожидаем 200)"):
        first_delete = api_manager.reviews_api.delete_review(movie_id, user_id)
        assert first_delete.status_code == 200, f"Ожидался 200, получен {first_delete.status_code}"

    with allure.step("Проверка, что отзыв удален из БД"):
        review_after_first = get_review_from_db(movie_id, user_id)
        assert review_after_first is None, "Отзыв остался в БД после первого удаления!"

    with allure.step("Второе удаление отзыва (ожидаем 404)"):
        second_delete = api_manager.reviews_api.delete_review(movie_id, user_id, expected_status=404)
        assert second_delete.status_code == 404, f"Ожидался 404, получен {second_delete.status_code}"
        allure.attach(str(second_delete.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Удаление отзывов")
@allure.story("Негативные сценарии - невалидный user_id")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_delete_review_invalid_user_id(api_manager, movie_payload):
    """Попытка удалить отзыв с невалидным user_id"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id)
        assert review_before is not None, "Отзыв не найден в БД!"

    with allure.step("DELETE запрос с невалидным user_id"):
        resp = api_manager.reviews_api.delete_review(movie_id, user_id="invalid-id", expected_status=404)

    with allure.step("Проверка статус-кода (400 или 404)"):
        assert resp.status_code in [400, 404], f"Ожидался 400 или 404, получен {resp.status_code}"
        allure.attach(str(resp.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв остался в БД (не был удален)"):
        review_after = get_review_from_db(movie_id)
        assert review_after is not None, "Отзыв был удален с невалидным user_id!"
        allure.attach("Отзыв остался в БД", name="DB After", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)