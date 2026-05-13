import requests

from conftest import movie_payload
from constants import BASE_URL, MOVIES_ENDPOINT


def test_get_reviews_by_movie_id(create_movie, movie_payload):
    # 1. создаем фильм
    create_response = create_movie(movie_payload())
    assert create_response.status_code == 201

    movie_id = create_response.json()["id"]

    # 2. получаем отзывы
    url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews"

    response = requests.get(url)

    # 3. проверки
    assert response.status_code == 200

    data = response.json()

    # ответ должен быть списком
    assert isinstance(data, list)

    # если есть отзывы — проверяем структуру
    if len(data) > 0:
        review = data[0]

        assert "userId" in review
        assert "rating" in review
        assert "text" in review
        assert "createdAt" in review
        assert "user" in review

        assert "fullName" in review["user"]