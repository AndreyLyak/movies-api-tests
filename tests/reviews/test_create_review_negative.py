import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_update_review_no_auth(api_manager, movie_payload):
    """Попытка обновить отзыв без авторизации"""
    # создаем фильм с отзывом
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201
    user_id = review_response.json()["userId"]

    url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews"
    response = requests.put(url, json={"rating": 4, "text": "updated"})
    assert response.status_code == 401


def test_update_review_not_found(api_manager):
    """Попытка обновить отзыв у несуществующего фильма"""
    response = api_manager.reviews_api.update_review(99999999, rating=4, text="test")
    assert response.status_code == 404


def test_update_review_invalid_rating(api_manager, movie_payload):
    """Попытка обновить отзыв с рейтингом больше 5"""
    # создаем фильм с отзывом
    create_response = api_manager.movies_api.create_movie(movie_payload())
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    response = api_manager.reviews_api.update_review(movie_id, rating=10, text="invalid rating")
    assert response.status_code in [200, 400, 422]


def test_update_review_negative_rating(api_manager, movie_payload):
    """Попытка обновить отзыв с отрицательным рейтингом"""
    create_response = api_manager.movies_api.create_movie(movie_payload())
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    response = api_manager.reviews_api.update_review(movie_id, rating=-1, text="negative rating")
    assert response.status_code in [200, 400, 422]


def test_update_review_empty_text(api_manager, movie_payload):
    """Попытка обновить отзыв с пустым текстом"""
    create_response = api_manager.movies_api.create_movie(movie_payload())
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    response = api_manager.reviews_api.update_review(movie_id, rating=4, text="")
    assert response.status_code in [200, 400, 422]


def test_update_review_missing_rating(api_manager, movie_payload):
    """Попытка обновить отзыв без рейтинга"""
    create_response = api_manager.movies_api.create_movie(movie_payload())
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    response = api_manager.reviews_api.update_review(movie_id, text="no rating")
    assert response.status_code in [200, 400]


def test_update_review_missing_text(api_manager, movie_payload):
    """Попытка обновить отзыв без текста"""
    create_response = api_manager.movies_api.create_movie(movie_payload())
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    response = api_manager.reviews_api.update_review(movie_id, rating=3)
    assert response.status_code in [200, 400]


def test_update_review_invalid_movie_id(api_manager):
    """Попытка обновить отзыв с невалидным movie_id"""
    response = api_manager.reviews_api.update_review("abc", rating=4, text="test")
    assert response.status_code in [400, 404]


def test_update_review_no_review_exists(api_manager, movie_payload):
    """Попытка обновить отзыв, которого не существует"""
    movie_resp = api_manager.movies_api.create_movie(movie_payload())
    movie_id = movie_resp.json()["id"]

    response = api_manager.reviews_api.update_review(movie_id, rating=4, text="no review")
    assert response.status_code == 404