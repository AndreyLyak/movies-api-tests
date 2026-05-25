import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_delete_review_no_auth(api_manager, movie_payload):
    """Попытка удалить отзыв без авторизации"""
    # создаем фильм с отзывом
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    resp = requests.delete(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews"
    )
    assert resp.status_code in [401, 403]


def test_delete_review_not_found(api_manager):
    """Попытка удалить отзыв у несуществующего фильма"""
    resp = api_manager.reviews_api.delete_review(999999)
    assert resp.status_code == 404


def test_delete_review_without_existing_review(api_manager, movie_payload):
    """Попытка удалить отзыв, которого не существует"""
    movie_resp = api_manager.movies_api.create_movie(movie_payload())
    movie_id = movie_resp.json()["id"]

    resp = api_manager.reviews_api.delete_review(movie_id)
    assert resp.status_code == 404


def test_delete_review_invalid_movie_id(api_manager):
    """Попытка удалить отзыв с невалидным movie_id"""
    resp = api_manager.reviews_api.delete_review("abc")
    assert resp.status_code in [400, 404]


def test_delete_review_double_delete(api_manager, movie_payload):
    """Попытка удалить отзыв дважды"""
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

    # удаляем первый раз
    assert api_manager.reviews_api.delete_review(movie_id, user_id).status_code == 200

    # удаляем второй раз
    assert api_manager.reviews_api.delete_review(movie_id, user_id).status_code == 404


def test_delete_review_invalid_user_id(api_manager, movie_payload):
    """Попытка удалить отзыв с невалидным user_id"""
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    resp = api_manager.reviews_api.delete_review(movie_id, user_id="invalid-id")
    assert resp.status_code in [400, 404]