# test_hide_review_negative.py (с комплексной фикстурой)
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_hide_review_no_auth(api_manager, movie_payload):
    """Попытка скрыть отзыв без авторизации"""
    # создаем фильм с отзывом
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    review_data = review_response.json()
    if isinstance(review_data, list):
        review_data = review_data[0]
    user_id = review_data.get("userId")

    resp = requests.patch(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews/hide/{user_id}"
    )
    assert resp.status_code in [401, 403]


def test_hide_review_not_found(api_manager):
    """Попытка скрыть отзыв у несуществующего фильма"""
    resp = api_manager.reviews_api.hide_review(999999, "some-user-id")
    assert resp.status_code == 404


def test_hide_review_invalid_user_id(api_manager, movie_payload):
    """Попытка скрыть отзыв с невалидным user_id"""
    # создаем фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    resp = api_manager.reviews_api.hide_review(movie_id, "invalid-id")
    assert resp.status_code in [400, 404]


def test_hide_review_already_hidden(api_manager, movie_payload):
    """Попытка скрыть уже скрытый отзыв"""
    # создаем фильм с отзывом
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    review_data = review_response.json()
    if isinstance(review_data, list):
        review_data = review_data[0]
    user_id = review_data.get("userId")

    # скрываем первый раз
    assert api_manager.reviews_api.hide_review(movie_id, user_id).status_code == 200

    # скрываем второй раз
    second_hide = api_manager.reviews_api.hide_review(movie_id, user_id)
    assert second_hide.status_code in [200, 400, 409]