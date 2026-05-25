#test_positive_get_reviews.py
from constants import MOVIES_ENDPOINT


def test_get_reviews_by_movie_id(api_manager, movie_payload):
    # 1. создаем фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201

    movie_id = create_response.json()["id"]

    # 2. получаем отзывы через api_manager
    response = api_manager.reviews_api.get_reviews(movie_id)

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