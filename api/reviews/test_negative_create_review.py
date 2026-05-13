import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_create_review_without_auth(create_movie, movie_payload):
    # создаем фильм
    response_movie = create_movie(movie_payload())
    movie_id = response_movie.json()["id"]

    # БЕЗ авторизации - прямой запрос
    url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews"
    response = requests.post(url, json={"rating": 5, "text": "Отзыв без авторизации"})
    assert response.status_code == 401


def test_create_review_nonexistent_movie(create_review):
    response = create_review(99999999, rating=5, text="Test")
    assert response.status_code == 404


def test_create_review_duplicate(create_movie, create_review, movie_payload):
    # создаем фильм
    response_movie = create_movie(movie_payload())
    movie_id = response_movie.json()["id"]

    payload = {"rating": 5, "text": "Один и тот же отзыв"}

    # первый раз — ок
    response1 = create_review(movie_id, **payload)
    assert response1.status_code in [200, 201]

    # второй раз — ошибка
    response2 = create_review(movie_id, **payload)
    assert response2.status_code == 409


def test_create_review_invalid_rating(create_movie, create_review, movie_payload):
    # создаем фильм
    response_movie = create_movie(movie_payload())
    movie_id = response_movie.json()["id"]

    response = create_review(movie_id, rating=10, text="Плохой рейтинг")
    assert response.status_code in [400, 422]


def test_create_review_empty_text(create_movie, create_review, movie_payload):
    # создаем фильм
    response_movie = create_movie(movie_payload())
    movie_id = response_movie.json()["id"]

    response = create_review(movie_id, rating=5, text="")
    assert response.status_code in [400, 422]