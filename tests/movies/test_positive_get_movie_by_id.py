def test_get_movie_by_id(api_manager, movie_payload):
    # сначала создаём фильм
    payload = movie_payload()
    create_response = api_manager.movies_api.create_movie(payload)
    assert create_response.status_code in [200, 201]
    movie_id = create_response.json()["id"]

    # получаем фильм
    get_response = api_manager.movies_api.get_movie(movie_id)
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["id"] == movie_id
    assert data["name"] == payload["name"]