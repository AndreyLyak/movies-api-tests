#test_hide_review_positive.py
def test_hide_review(api_manager, movie_payload):
    # 1. создаем фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    # 2. создаем отзыв
    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    review_data = review_response.json()
    if isinstance(review_data, list):
        review_data = review_data[0]
    user_id = review_data.get("userId")
    review_text = review_data.get("text")

    # 3. скрываем отзыв
    hide_resp = api_manager.reviews_api.hide_review(movie_id, user_id)
    assert hide_resp.status_code == 200

    result = hide_resp.json()

    # 4. проверки
    assert result["userId"] == user_id
    assert result["text"] == review_text

    if "hidden" in result:
        assert result["hidden"] is True