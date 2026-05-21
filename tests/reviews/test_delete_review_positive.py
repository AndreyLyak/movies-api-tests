def test_delete_review(create_movie_with_review, delete_review, get_reviews):
    # создаем фильм с отзывом
    data = create_movie_with_review()

    # удаляем отзыв
    delete_resp = delete_review(data["movie_id"], data["user_id"])
    assert delete_resp.status_code == 200

    # проверяем, что отзыв удален
    get_resp = get_reviews(data["movie_id"])
    assert get_resp.status_code == 200

    reviews = get_resp.json()
    for review in reviews:
        assert review["text"] != data["review_data"]["text"]