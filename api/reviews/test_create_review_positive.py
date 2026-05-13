# test_create_review_positive.py

def test_update_review(create_movie_with_review, update_review):
    # 1. создаем фильм с отзывом
    data = create_movie_with_review()

    # 2. обновляем отзыв
    update_payload = {
        "rating": 4,
        "text": f"updated text"
    }

    update_resp = update_review(data["movie_id"], **update_payload)
    assert update_resp.status_code == 200

    # 3. проверяем результат
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
            assert review.get("userId") == data["user_id"]

    assert found, f"Updated review not found in response: {result}"