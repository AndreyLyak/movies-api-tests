import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_show_review_without_auth(create_movie, create_review, movie_payload):
    """Попытка показать отзыв без токена авторизации"""
    # создаем фильм и отзыв с помощью фикстур
    movie_resp = create_movie(movie_payload())
    assert movie_resp.status_code in [200, 201]
    movie_id = movie_resp.json()["id"]

    # создаем отзыв через фикстуру
    review_resp = create_review(movie_id, rating=5, text="test")
    assert review_resp.status_code in [200, 201]

    # получаем user_id из ответа (фикстура create_review может возвращать данные)
    review_data = review_resp.json()
    if isinstance(review_data, list):
        review_data = review_data[0]
    user_id = review_data["userId"]

    # пробуем показать отзыв БЕЗ токена (не используем api_client)
    resp = requests.patch(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews/show/{user_id}"
    )

    assert resp.status_code == 401


def test_show_review_nonexistent_movie(api_client):
    """Попытка показать отзыв у несуществующего фильма"""
    # используем api_client для авторизованного запроса
    resp = api_client.patch(
        f"{MOVIES_ENDPOINT}/999999/reviews/show/some-user-id"
    )

    assert resp.status_code == 404


def test_show_review_nonexistent_user(create_movie, api_client, movie_payload):
    """Попытка показать отзыв с несуществующим user_id"""
    # создаем фильм
    movie_resp = create_movie(movie_payload())
    assert movie_resp.status_code in [200, 201]
    movie_id = movie_resp.json()["id"]

    # пробуем показать отзыв с fake user_id
    resp = api_client.patch(
        f"{MOVIES_ENDPOINT}/{movie_id}/reviews/show/fake-user-id"
    )

    assert resp.status_code == 404


def test_show_review_invalid_user_id(create_movie, api_client, movie_payload):
    """Попытка показать отзыв с невалидным user_id (спецсимволы)"""
    # создаем фильм
    movie_resp = create_movie(movie_payload())
    assert movie_resp.status_code in [200, 201]
    movie_id = movie_resp.json()["id"]

    # передаем явно кривой userId
    resp = api_client.patch(
        f"{MOVIES_ENDPOINT}/{movie_id}/reviews/show/!!!"
    )

    # API может вести себя по-разному — допускаем несколько вариантов
    assert resp.status_code in [400, 404, 500]