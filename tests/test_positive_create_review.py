# test_positive_create_review.py
from constants import MOVIES_ENDPOINT


def test_create_review(create_movie, api_client, movie_payload):
    # 1. создаем фильм
    create_response = create_movie(movie_payload())
    assert create_response.status_code in [200, 201]

    movie_id = create_response.json()["id"]

    # 2. создаем отзыв напрямую через api_client
    review_data = {
        "rating": 4,
        "text": "Хорошее кино"
    }

    response = api_client.post(
        f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
        json=review_data
    )

    # 3. проверки
    assert response.status_code in [200, 201]

    data = response.json()

    assert isinstance(data, dict)
    assert data["rating"] == review_data["rating"]
    assert data["text"] == review_data["text"]
    assert "userId" in data
    assert "createdAt" in data
    assert "user" in data
    assert "fullName" in data["user"]