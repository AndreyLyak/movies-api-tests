def test_create_movie(create_movie, movie_payload):
    # Создаем фильм через фикстуру
    payload = movie_payload()
    response = create_movie(payload)

    assert response.status_code in [200, 201]

    data = response.json()

    assert "id" in data
    assert data["name"] == payload["name"]