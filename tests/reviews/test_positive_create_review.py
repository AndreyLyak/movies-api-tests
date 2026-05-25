# test_positive_create_review.py
def test_create_review(api_manager, movie_payload):
    # 1. создаем фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code in [200, 201]
    movie_id = create_response.json()["id"]

    # 2. создаем отзыв через api_manager
    review_data = {
        "rating": 4,
        "text": "Хорошее кино"
    }

    response = api_manager.reviews_api.create_review(
        movie_id,
        rating=review_data["rating"],
        text=review_data["text"]
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