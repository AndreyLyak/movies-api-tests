def test_hide_review(create_movie_with_review, hide_review):
    # 1. создаем фильм с отзывом одной фикстурой!
    data = create_movie_with_review()

    # 2. скрываем отзыв
    hide_resp = hide_review(data["movie_id"], data["user_id"])
    assert hide_resp.status_code == 200

    result = hide_resp.json()

    # 3. проверки
    assert result["userId"] == data["user_id"]
    assert result["text"] == data["review_data"]["text"]

    if "hidden" in result:
        assert result["hidden"] is True