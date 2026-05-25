def test_update_review(api_manager, movie_payload):
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

    # 3. обновляем отзыв
    update_payload = {
        "rating": 4,
        "text": "updated text"
    }

    update_resp = api_manager.reviews_api.update_review(movie_id, rating=4, text="updated text")
    assert update_resp.status_code == 200

    # 4. проверяем результат
    result = update_resp.json()

    # API может вернуть объект или список
    reviews = result if isinstance(result, list) else [result]

    # ищем обновленный отзыв
    found = False
    for review in reviews:
        if review.get("text") == update_payload["text"]:
            found = True
            assert review.get("rating") == update_payload["rating"]
            assert "createdAt" in review
            assert "movieId" in review
            assert review.get("userId") == user_id

    assert found, f"Updated review not found in response: {result}"