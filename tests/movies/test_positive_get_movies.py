#test_positive_get_movies.py
def test_movie_structure(api_manager, movie_payload):
    """
    Позитивный тест: проверяем структуру фильма.
    Создаём фильм, затем получаем его по ID и проверяем поля.
    """
    # 1. Создаём тестовый фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code in [200, 201]
    movie_id = create_response.json()["id"]

    try:
        # 2. Получаем фильм напрямую по ID (без поиска в списке!)
        get_response = api_manager.movies_api.get_movie(movie_id)
        assert get_response.status_code == 200
        movie = get_response.json()

        # 3. Проверяем структуру фильма
        assert "id" in movie
        assert "name" in movie
        assert "price" in movie
        assert "location" in movie
    finally:
        # 4. Очистка (удаляем созданный фильм)
        api_manager.movies_api.delete_movie(movie_id)