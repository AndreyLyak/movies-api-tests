import uuid


def test_demo_create_movie_via_api_manager(api_manager):
    """
    Демонстрация: создание фильма через ApiManager.
    Показывает, что новая архитектура работает.
    """
    # Генерируем данные для фильма
    movie_data = {
        "name": f"Demo Movie {uuid.uuid4()}",
        "imageUrl": "https://img.com",
        "price": 100,
        "description": "Test via ApiManager",
        "location": "SPB",
        "published": True,
        "genreId": 1
    }

    # СОЗДАЕМ фильм через ApiManager
    response = api_manager.movies_api.create_movie(movie_data)
    assert response.status_code == 201

    movie_id = response.json()["id"]

    # ПОЛУЧАЕМ фильм через ApiManager
    get_response = api_manager.movies_api.get_movie(movie_id)
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["name"] == movie_data["name"]
    assert data["id"] == movie_id

    # УДАЛЯЕМ фильм через ApiManager (чистка)
    api_manager.movies_api.delete_movie(movie_id)