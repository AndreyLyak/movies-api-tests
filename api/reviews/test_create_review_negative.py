import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_update_review_no_auth(create_movie_with_review):
    """Попытка обновить отзыв без авторизации"""
    data = create_movie_with_review()

    url = f"{BASE_URL}{MOVIES_ENDPOINT}/{data['movie_id']}/reviews"
    response = requests.put(url, json={"rating": 4, "text": "updated"})
    assert response.status_code == 401


def test_update_review_not_found(update_review):
    """Попытка обновить отзыв у несуществующего фильма"""
    response = update_review(99999999, rating=4, text="test")
    assert response.status_code == 404


def test_update_review_invalid_rating(create_movie_with_review, update_review):
    """Попытка обновить отзыв с рейтингом больше 5"""
    data = create_movie_with_review()

    response = update_review(data["movie_id"], rating=10, text="invalid rating")
    assert response.status_code in [400, 422]


def test_update_review_negative_rating(create_movie_with_review, update_review):
    """Попытка обновить отзыв с отрицательным рейтингом"""
    data = create_movie_with_review()

    response = update_review(data["movie_id"], rating=-1, text="negative rating")
    assert response.status_code in [400, 422]


def test_update_review_empty_text(create_movie_with_review, update_review):
    """Попытка обновить отзыв с пустым текстом"""
    data = create_movie_with_review()

    response = update_review(data["movie_id"], rating=4, text="")
    assert response.status_code in [400, 422]


def test_update_review_missing_rating(create_movie_with_review, update_review):
    """Попытка обновить отзыв без рейтинга"""
    data = create_movie_with_review()

    # передаем только текст, без рейтинга
    response = update_review(data["movie_id"], text="no rating")
    # может быть 200 (если рейтинг опционален) или 400
    assert response.status_code in [200, 400]


def test_update_review_missing_text(create_movie_with_review, update_review):
    """Попытка обновить отзыв без текста"""
    data = create_movie_with_review()

    # передаем только рейтинг, без текста
    response = update_review(data["movie_id"], rating=3)
    # может быть 200 (если текст опционален) или 400
    assert response.status_code in [200, 400]


def test_update_review_invalid_movie_id(update_review):
    """Попытка обновить отзыв с невалидным movie_id"""
    response = update_review("abc", rating=4, text="test")
    assert response.status_code in [400, 404]


def test_update_review_no_review_exists(create_movie, update_review, movie_payload):
    """Попытка обновить отзыв, которого не существует"""
    movie_resp = create_movie(movie_payload())
    movie_id = movie_resp.json()["id"]

    response = update_review(movie_id, rating=4, text="no review")
    assert response.status_code == 404