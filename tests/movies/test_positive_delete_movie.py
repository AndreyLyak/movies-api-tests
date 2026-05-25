def test_positive_delete_movie(api_manager, movie_payload):
    # создаем фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code in [200, 201]
    movie_id = create_response.json()["id"]

    # удаляем
    delete_response = api_manager.movies_api.delete_movie(movie_id)
    assert delete_response.status_code == 200

    # проверяем, что фильм удален
    get_response = api_manager.movies_api.get_movie(movie_id)
    assert get_response.status_code == 404