# tests/reviews/test_delete_review_positive.py
import pytest
import allure
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
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_delete_review(api_manager, movie_payload):
    """Позитивный тест: удаление отзыва"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201, f"Ожидался 201, получен {create_response.status_code}"
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Test review for deletion")
        assert review_response.status_code == 201, f"Ожидался 201, получен {review_response.status_code}"

        review_data = review_response.json()
        if isinstance(review_data, list):
            review_data = review_data[0]

        user_id = review_data.get("userId")
        review_text = review_data.get("text")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(review_data), name="Created Review", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыв появился в БД"):
        review_before = get_review_from_db(movie_id, user_id)
        assert review_before is not None, "Отзыв не найден в БД!"
        assert review_before["text"] == review_text, "Текст в БД не совпадает"
        allure.attach("Отзыв успешно создан в БД", name="DB Before", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Удаление отзыва (ожидаем 200)"):
        delete_resp = api_manager.reviews_api.delete_review(movie_id, user_id)
        assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
        allure.attach(str(delete_resp.json()), name="Delete Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыв удален из БД"):
        review_after = get_review_from_db(movie_id, user_id)
        assert review_after is None, f"Отзыв с текстом '{review_text}' остался в БД!"
        allure.attach("Отзыв успешно удален из БД", name="DB After", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        delete_movie_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_movie_resp.status_code == 200, f"Ожидался 200, получен {delete_movie_resp.status_code}"
        allure.attach(f"Фильм {movie_id} удален", name="Cleanup", attachment_type=allure.attachment_type.TEXT)
