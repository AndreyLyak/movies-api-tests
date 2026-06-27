# tests/reviews/test_show_review_positive.py
import pytest
import allure
import uuid
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

    with allure.step("Проверка, что отзыв есть в БД"):
        review_before = get_review_from_db(movie_id, user_id)
        assert review_before is not None, "Отзыв не найден в БД!"
        allure.attach("Отзыв есть в БД", name="DB Before", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Скрытие отзыва"):
        hide_resp = api_manager.reviews_api.hide_review(movie_id, user_id)
        assert hide_resp.status_code == 200, f"Ожидался 200, получен {hide_resp.status_code}"
        allure.attach(str(hide_resp.json()), name="Hide Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыв скрыт в БД (если есть поле hidden)"):
        review_after_hide = get_review_from_db(movie_id, user_id)
        assert review_after_hide is not None, "Отзыв исчез из БД!"
        if "hidden" in review_after_hide:
            assert review_after_hide["hidden"] is True or review_after_hide["hidden"] == 1, "Отзыв не был скрыт в БД!"
            allure.attach("Отзыв скрыт в БД", name="DB After Hide", attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach("Поле hidden отсутствует в БД", name="DB Info", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Показ отзыва обратно"):
        show_resp = api_manager.reviews_api.show_review(movie_id, user_id)
        assert show_resp.status_code == 200, f"Ожидался 200, получен {show_resp.status_code}"

    with allure.step("Получение данных показанного отзыва из API"):
        data = show_resp.json()
        allure.attach(str(data), name="Show Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что отзыв показан в БД (если есть поле hidden)"):
        review_after_show = get_review_from_db(movie_id, user_id)
        assert review_after_show is not None, "Отзыв исчез из БД!"
        if "hidden" in review_after_show:
            assert review_after_show["hidden"] is False or review_after_show["hidden"] == 0, "Отзыв не был показан в БД!"
            allure.attach("Отзыв показан в БД", name="DB After Show", attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach("Поле hidden отсутствует в БД", name="DB Info", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка данных отзыва в ответе API"):
        assert data["userId"] == user_id, f"userId не совпадает: ожидался {user_id}, получен {data['userId']}"
        assert "rating" in data, "Поле 'rating' отсутствует"
        assert "text" in data, "Поле 'text' отсутствует"
        assert "createdAt" in data, "Поле 'createdAt' отсутствует"
        allure.attach("Все проверки пройдены", name="Success", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        delete_resp = api_manager.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
        allure.attach(f"Фильм {movie_id} удален", name="Cleanup", attachment_type=allure.attachment_type.TEXT)
