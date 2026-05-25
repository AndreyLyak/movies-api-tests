#test_show_review_positive.py
def test_show_review(api_manager, movie_payload):
    # 1. создаем фильм
    movie_resp = api_manager.movies_api.create_movie(movie_payload())
    assert movie_resp.status_code in [200, 201]
    movie_id = movie_resp.json()["id"]

    # 2. создаем отзыв
    review_resp = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_resp.status_code in [200, 201]

    review_data = review_resp.json()
    if isinstance(review_data, list):
        review_data = review_data[0]
    user_id = review_data["userId"]

    # 3. скрываем отзыв
    hide_resp = api_manager.reviews_api.hide_review(movie_id, user_id)
    assert hide_resp.status_code == 200

    # 4. показываем отзыв обратно
    show_resp = api_manager.reviews_api.show_review(movie_id, user_id)
    assert show_resp.status_code == 200

    data = show_resp.json()

    # 5. проверки
    assert data["userId"] == user_id
    assert "rating" in data
    assert "text" in data
    assert "createdAt" in data