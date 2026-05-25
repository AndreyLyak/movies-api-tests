#test_delete_review_posotive.py

def test_delete_review(api_manager, movie_payload):
    # создаем фильм с отзывом
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    review_response = api_manager.reviews_api.create_review(movie_id, rating=5)
    assert review_response.status_code == 201

    review_data = review_response.json()
    if isinstance(review_data, list):
        review_data = review_data[0]
    user_id = review_data.get("userId")
    review_text = review_data.get("text")

    # удаляем отзыв
    delete_resp = api_manager.reviews_api.delete_review(movie_id, user_id)
    assert delete_resp.status_code == 200

    # проверяем, что отзыв удален
    get_resp = api_manager.reviews_api.get_reviews(movie_id)
    assert get_resp.status_code == 200

    reviews = get_resp.json()
    for review in reviews:
        assert review["text"] != review_text