# test_delete_review_negative.py (супер-чистая версия)
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_delete_review_no_auth(create_movie_with_review):
    """Попытка удалить отзыв без авторизации"""
    data = create_movie_with_review()

    resp = requests.delete(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{data['movie_id']}/reviews"
    )
    assert resp.status_code in [401, 403]


def test_delete_review_not_found(api_client):
    """Попытка удалить отзыв у несуществующего фильма"""
    resp = api_client.delete(f"{MOVIES_ENDPOINT}/999999/reviews")
    assert resp.status_code == 404


def test_delete_review_without_existing_review(create_movie, api_client, movie_payload):
    """Попытка удалить отзыв, которого не существует"""
    movie_resp = create_movie(movie_payload())
    movie_id = movie_resp.json()["id"]

    resp = api_client.delete(f"{MOVIES_ENDPOINT}/{movie_id}/reviews")
    assert resp.status_code == 404


def test_delete_review_invalid_movie_id(api_client):
    """Попытка удалить отзыв с невалидным movie_id"""
    resp = api_client.delete(f"{MOVIES_ENDPOINT}/abc/reviews")
    assert resp.status_code in [400, 404]


def test_delete_review_double_delete(create_movie_with_review, delete_review):
    """Попытка удалить отзыв дважды"""
    data = create_movie_with_review()

    # удаляем первый раз
    assert delete_review(data["movie_id"], data["user_id"]).status_code == 200

    # удаляем второй раз
    assert delete_review(data["movie_id"], data["user_id"]).status_code == 404


def test_delete_review_invalid_user_id(create_movie_with_review, api_client):
    """Попытка удалить отзыв с невалидным user_id"""
    data = create_movie_with_review()

    resp = api_client.delete(
        f"{MOVIES_ENDPOINT}/{data['movie_id']}/reviews",
        params={"userId": "invalid-id"}
    )
    assert resp.status_code in [400, 404]