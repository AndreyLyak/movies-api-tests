# Movies/tests/test_positive_patch_movies.py
import uuid


def test_update_movie(create_movie, update_movie, movie_payload):
    # 1. CREATE фильм
    create_response = create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    # 2. UPDATE фильм - используем специальную фикстуру
    update_data = {
        "name": f"Updated Movie {uuid.uuid4()}",
        "description": "Updated description",
        "price": 200,
        "location": "MSK",
        "imageUrl": "https://new-image.url",
        "published": False
    }

    update_response = update_movie(movie_id, **update_data)
    assert update_response.status_code == 200

    data = update_response.json()

    # 3. ПРОВЕРКИ
    assert data["id"] == movie_id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["price"] == update_data["price"]
    assert data["location"] == update_data["location"]
    assert data["imageUrl"] == update_data["imageUrl"]
    assert data["published"] == update_data["published"]
    # genreId должен остаться неизменным
    assert data["genreId"] == 1  # значение из movie_payload по умолчанию