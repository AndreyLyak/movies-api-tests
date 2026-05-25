def test_create_movie(api_manager, movie_payload):
    # Создаем фильм через фикстуру
    payload = movie_payload()
    response = api_manager.movies_api.create_movie(movie_payload())

    assert response.status_code in [200, 201]

    data = response.json()

    assert "id" in data
    assert data["name"] == payload["name"]