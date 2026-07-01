# tests/reviews/test_create_review_negative.py
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
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - авторизация")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_update_review_no_auth(api_manager, movie_payload):
    """Попытка обновить отзыв без авторизации"""

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
        original_text = review_data.get("text")
        original_rating = review_data.get("rating")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id, user_id)
        assert review_before is not None, "Отзыв не найден в БД!"

    with allure.step("PUT запрос без токена авторизации"):
        url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews"
        response = requests.put(url, json={"rating": 4, "text": "updated"})

    with allure.step("Проверка статус-кода 401"):
        assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что отзыв НЕ изменился в БД"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is not None, "Отзыв исчез из БД!"
        assert review_after["text"] == original_text, "Текст изменился без авторизации!"
        assert review_after["rating"] == original_rating, "Рейтинг изменился без авторизации!"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - несуществующий фильм")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_not_found(api_manager):
    """Попытка обновить отзыв у несуществующего фильма"""

    with allure.step("PUT запрос с несуществующим movie_id"):
        response = api_manager.reviews_api.update_review(99999999, rating=4, text="test", expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - невалидные данные")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_invalid_rating(api_manager, movie_payload):
    """Попытка обновить отзыв с рейтингом больше 5 (ожидаем 400)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва с рейтингом 5"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201
        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        original_rating = review_data.get("rating")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PUT запрос с рейтингом 10 (ожидаем 400)"):
        response = api_manager.reviews_api.update_review(movie_id, rating=10, text="invalid rating", expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что рейтинг НЕ изменился в БД"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is not None, "Отзыв не найден в БД!"
        assert review_after["rating"] == original_rating, f"Рейтинг изменился: {original_rating} -> {review_after['rating']}"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - невалидные данные")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_negative_rating(api_manager, movie_payload):
    """Попытка обновить отзыв с отрицательным рейтингом (ожидаем 400)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201
        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        original_rating = review_data.get("rating")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PUT запрос с отрицательным рейтингом (ожидаем 400)"):
        response = api_manager.reviews_api.update_review(movie_id, rating=-1, text="negative rating", expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что рейтинг НЕ изменился в БД"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is not None, "Отзыв не найден в БД!"
        assert review_after["rating"] == original_rating, f"Рейтинг изменился: {original_rating} -> {review_after['rating']}"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - пустые поля")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_empty_text(api_manager, movie_payload):
    """Попытка обновить отзыв с пустым текстом (ожидаем 400)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201
        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        original_text = review_data.get("text")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PUT запрос с пустым текстом (ожидаем 400)"):
        response = api_manager.reviews_api.update_review(movie_id, rating=4, text="", expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что текст НЕ изменился в БД"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is not None, "Отзыв не найден в БД!"
        assert review_after["text"] == original_text, f"Текст изменился: {original_text} -> {review_after['text']}"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - отсутствуют поля")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_missing_rating(api_manager, movie_payload):
    """Попытка обновить отзыв без рейтинга (ожидаем 400)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201
        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        original_rating = review_data.get("rating")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PUT запрос без рейтинга (ожидаем 400)"):
        response = api_manager.reviews_api.update_review(movie_id, text="no rating", expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что рейтинг НЕ изменился в БД"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is not None, "Отзыв исчез из БД!"
        assert review_after["rating"] == original_rating, f"Рейтинг изменился: {original_rating} -> {review_after['rating']}"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - отсутствуют поля")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_missing_text(api_manager, movie_payload):
    """Попытка обновить отзыв без текста (ожидаем 400)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201
        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]
        user_id = review_data.get("userId")
        original_text = review_data.get("text")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PUT запрос без текста (ожидаем 400)"):
        response = api_manager.reviews_api.update_review(movie_id, rating=3, expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что текст НЕ изменился в БД"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is not None, "Отзыв исчез из БД!"
        assert review_after["text"] == original_text, f"Текст изменился: {original_text} -> {review_after['text']}"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - невалидный ID")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_invalid_movie_id(api_manager):
    """Попытка обновить отзыв с невалидным movie_id"""

    with allure.step("PUT запрос с невалидным movie_id 'abc'"):
        response = api_manager.reviews_api.update_review("abc", rating=4, text="test", expected_status=404)

    with allure.step("Проверка статус-кода (400 или 404)"):
        assert response.status_code in [400, 404], f"Ожидался 400 или 404, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - отсутствует отзыв")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_no_review_exists(api_manager, movie_payload):
    """Попытка обновить отзыв, которого не существует"""

    with allure.step("Создание фильма через API"):
        movie_resp = api_manager.movies_api.create_movie(movie_payload())
        movie_id = movie_resp.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PUT запрос без создания отзыва (ожидаем 404)"):
        response = api_manager.reviews_api.update_review(movie_id, rating=4, text="no review", expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыва нет в БД"):
        review = get_review_from_db(movie_id)
        assert review is None, "Отзыв появился в БД, хотя не должен был!"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)