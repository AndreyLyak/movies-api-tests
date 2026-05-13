# test_hide_review_negative.py (с комплексной фикстурой)
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_hide_review_no_auth(create_movie_with_review):
    """Попытка скрыть отзыв без авторизации"""
    data = create_movie_with_review()

    resp = requests.patch(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{data['movie_id']}/reviews/hide/{data['user_id']}"
    )
    assert resp.status_code in [401, 403]


def test_hide_review_not_found(api_client):
    """Попытка скрыть отзыв у несуществующего фильма"""
    resp = api_client.patch(f"{MOVIES_ENDPOINT}/999999/reviews/hide/some-user-id")
    assert resp.status_code == 404


def test_hide_review_invalid_user_id(create_movie_with_review, api_client):
    """Попытка скрыть отзыв с невалидным user_id"""
    data = create_movie_with_review()

    resp = api_client.patch(f"{MOVIES_ENDPOINT}/{data['movie_id']}/reviews/hide/invalid-id")
    assert resp.status_code in [400, 404]


def test_hide_review_already_hidden(create_movie_with_review, hide_review):
    """Попытка скрыть уже скрытый отзыв"""
    data = create_movie_with_review()

    # скрываем первый раз
    assert hide_review(data["movie_id"], data["user_id"]).status_code == 200

    # скрываем второй раз
    second_hide = hide_review(data["movie_id"], data["user_id"])
    assert second_hide.status_code in [200, 400, 409]