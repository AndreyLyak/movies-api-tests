# tests/reviews/test_negative_create_review.py
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
@allure.feature("Создание отзывов")
@allure.story("Негативные сценарии - авторизация")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_create_review_without_auth(api_manager, movie_payload):
    """Попытка создать отзыв без авторизации"""

    with allure.step("Создание фильма через API"):
        response_movie = api_manager.movies_api.create_movie(movie_payload())
        assert response_movie.status_code == 201
        movie_id = response_movie.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что у фильма нет отзывов"):
        review_before = get_review_from_db(movie_id)
        assert review_before is None, "У фильма уже есть отзывы!"

    with allure.step("POST запрос без токена авторизации"):
        url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews"
        response = requests.post(url, json={"rating": 5, "text": "Отзыв без авторизации"})

    with allure.step("Проверка статус-кода 401"):
        assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв НЕ создался в БД"):
        review_after = get_review_from_db(movie_id)
        assert review_after is None, "Отзыв создался без авторизации!"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Создание отзывов")
@allure.story("Негативные сценарии - несуществующий фильм")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_create_review_nonexistent_movie(api_manager):
    """Попытка создать отзыв для несуществующего фильма"""

    with allure.step("POST запрос с несуществующим movie_id"):
        response = api_manager.reviews_api.create_review(99999999, rating=5, text="Test", expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Reviews")
@allure.feature("Создание отзывов")
@allure.story("Негативные сценарии - дубликат")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_create_review_duplicate(api_manager, movie_payload):
    """Попытка создать два одинаковых отзыва для одного фильма"""

    with allure.step("Создание фильма через API"):
        response_movie = api_manager.movies_api.create_movie(movie_payload())
        assert response_movie.status_code == 201
        movie_id = response_movie.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    payload = {"rating": 5, "text": "Один и тот же отзыв"}
    allure.attach(str(payload), name="Review Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Первое создание отзыва (ожидаем 200 или 201)"):
        response1 = api_manager.reviews_api.create_review(movie_id, **payload)
        assert response1.status_code in [200, 201], f"Ожидался 200 или 201, получен {response1.status_code}"
        review_data = response1.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв появился в БД"):
        review_before = get_review_from_db(movie_id, user_id)
        assert review_before is not None, "Отзыв не найден в БД!"
        assert review_before["text"] == payload["text"], "Текст в БД не совпадает"

    with allure.step("Второе создание отзыва (ожидаем 409 Conflict)"):
        response2 = api_manager.reviews_api.create_review(movie_id, **payload, expected_status=409)

    with allure.step("Проверка статус-кода 409"):
        assert response2.status_code == 409, f"Ожидался 409, получен {response2.status_code}"
        allure.attach(str(response2.json()), name="Conflict Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что в БД только один отзыв"):
        session = SessionLocal()
        try:
            query = "SELECT COUNT(*) FROM reviews WHERE movie_id = :movie_id"
            result = session.execute(text(query), {"movie_id": movie_id}).fetchone()
            count = result[0] if result else 0
            assert count == 1, f"В БД {count} отзывов, должно быть 1"
        finally:
            session.close()
        allure.attach("В БД только один отзыв", name="DB Check", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Создание отзывов")
@allure.story("Негативные сценарии - невалидные данные")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_create_review_invalid_rating(api_manager, movie_payload):
    """Попытка создать отзыв с рейтингом больше 5 (ожидаем 400)"""

    with allure.step("Создание фильма через API"):
        response_movie = api_manager.movies_api.create_movie(movie_payload())
        assert response_movie.status_code == 201
        movie_id = response_movie.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что у фильма нет отзывов"):
        review_before = get_review_from_db(movie_id)
        assert review_before is None, "У фильма уже есть отзывы!"

    with allure.step("Создание отзыва с рейтингом 10 (ожидаем 400)"):
        response = api_manager.reviews_api.create_review(movie_id, rating=10, text="Плохой рейтинг", expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыв НЕ создался в БД"):
        review_after = get_review_from_db(movie_id)
        assert review_after is None, "Отзыв создался с невалидным рейтингом!"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Создание отзывов")
@allure.story("Негативные сценарии - пустые поля")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_create_review_empty_text(api_manager, movie_payload):
    """Попытка создать отзыв с пустым текстом (ожидаем 400)"""

    with allure.step("Создание фильма через API"):
        response_movie = api_manager.movies_api.create_movie(movie_payload())
        assert response_movie.status_code == 201
        movie_id = response_movie.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что у фильма нет отзывов"):
        review_before = get_review_from_db(movie_id)
        assert review_before is None, "У фильма уже есть отзывы!"

    with allure.step("Создание отзыва с пустым текстом (ожидаем 400)"):
        response = api_manager.reviews_api.create_review(movie_id, rating=5, text="", expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыв НЕ создался в БД"):
        review_after = get_review_from_db(movie_id)
        assert review_after is None, "Отзыв создался с пустым текстом!"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)