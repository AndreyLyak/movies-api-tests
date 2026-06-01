#test_positive_get_reviews.py
import uuid

def test_get_reviews_by_movie_id(api_manager, movie_payload):
    # 1. Создаём фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    # 2. Создаём отзыв для этого фильма (обязательный шаг!)
    review_payload = {
        "rating": 5,
        "text": f"Test review {uuid.uuid4()}"
    }
    create_review_resp = api_manager.reviews_api.create_review(movie_id, **review_payload)
    assert create_review_resp.status_code in [200, 201]

    # 3. Получаем отзывы
    response = api_manager.reviews_api.get_reviews(movie_id)
    assert response.status_code == 200

    data = response.json()

    # 4. Проверяем, что отзыв появился
    assert isinstance(data, list)
    assert len(data) > 0, "Ожидаем хотя бы один отзыв после создания"

    # 5. Проверяем структуру первого отзыва
    review = data[0]
    assert "userId" in review
    assert "rating" in review
    assert "text" in review
    assert "createdAt" in review
    assert "user" in review
    assert "fullName" in review["user"]

    # 6. (Опционально) Проверяем, что созданный отзыв действительно в списке
    assert review["rating"] == review_payload["rating"]
    assert review["text"] == review_payload["text"]