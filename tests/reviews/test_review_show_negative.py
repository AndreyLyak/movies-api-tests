#test_review_show_negative.py
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_show_review_without_auth(api_manager, movie_payload):
    """Попытка показать отзыв без токена авторизации"""
    # создаем фильм
    movie_resp = api_manager.movies_api.create_movie(movie_payload())
    assert movie_resp.status_code in [200, 201]
    movie_id = movie_resp.json()["id"]

    # создаем отзыв
    review_resp = api_manager.reviews_api.create_review(movie_id, rating=5, text="test")
    assert review_resp.status_code in [200, 201]

    # получаем user_id из ответа
    review_data = review_resp.json()
    if isinstance(review_data, list):
        review_data = review_data[0]
    user_id = review_data["userId"]

    # пробуем показать отзыв БЕЗ токена
    resp = requests.patch(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews/show/{user_id}"
    )
    assert resp.status_code == 401


def test_show_review_nonexistent_movie(api_manager):
    """Попытка показать отзыв у несуществующего фильма"""
    resp = api_manager.reviews_api.show_review(999999, "some-user-id")
    assert resp.status_code == 404


def test_show_review_nonexistent_user(api_manager, movie_payload):
    """Попытка показать отзыв с несуществующим user_id"""
    # создаем фильм
    movie_resp = api_manager.movies_api.create_movie(movie_payload())
    assert movie_resp.status_code in [200, 201]
    movie_id = movie_resp.json()["id"]

    # пробуем показать отзыв с fake user_id
    resp = api_manager.reviews_api.show_review(movie_id, "fake-user-id")
    assert resp.status_code == 404


def test_show_review_invalid_user_id(api_manager, movie_payload):
    """Попытка показать отзыв с невалидным user_id (спецсимволы)"""
    # создаем фильм
    movie_resp = api_manager.movies_api.create_movie(movie_payload())
    assert movie_resp.status_code in [200, 201]
    movie_id = movie_resp.json()["id"]

    # передаем явно кривой userId
    resp = api_manager.reviews_api.show_review(movie_id, "!!!")
    assert resp.status_code in [400, 404, 500]