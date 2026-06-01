import pytest


def test_get_movies_default(api_manager):
    """Проверяем, что API работает без параметров"""
    response = api_manager.movies_api.get_movies()
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data


def test_pagination(api_manager):
    """Проверяем pageSize и page из сваггера"""
    response = api_manager.movies_api.get_movies(params={"page": 2, "pageSize": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["pageSize"] == 5


def test_filter_price(api_manager):
    """Фильтр по цене"""
    response = api_manager.movies_api.get_movies(params={"minPrice": 100, "maxPrice": 500})
    assert response.status_code == 200
    data = response.json()
    for movie in data["movies"]:
        assert 100 <= movie["price"] <= 500
    assert "movies" in data


@pytest.mark.parametrize("created_at", ["asc", "desc"])
def test_sort(api_manager, created_at):
    """Проверка сортировки"""
    response = api_manager.movies_api.get_movies(params={"createdAt": created_at})
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data


def test_movie_structure(api_manager, movie_payload):
    """Проверка структуры фильма (с созданием тестового фильма)"""
    # Создаем тестовый фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    created_movie_id = create_response.json()["id"]

    try:
        # Получаем список фильмов
        response = api_manager.movies_api.get_movies()
        assert response.status_code == 200
        data = response.json()

        assert "movies" in data
        assert len(data["movies"]) > 0, "Список фильмов не должен быть пустым"

        # Проверяем структуру первого фильма
        movie = data["movies"][0]
        assert "id" in movie
        assert "name" in movie
        assert "price" in movie
        assert "location" in movie
    finally:
        # Очистка (удаляем созданный фильм)
        api_manager.movies_api.delete_movie(created_movie_id)


def test_filter_published(api_manager):
    """Проверка фильтра по published"""
    response = api_manager.movies_api.get_movies(params={"published": True})
    data = response.json()
    for movie in data["movies"]:
        assert movie["published"] is True


def test_filter_location(api_manager):
    """Проверка фильтра по локации"""
    response = api_manager.movies_api.get_movies(params={"location": "MSK"})
    data = response.json()
    if data["movies"]:
        for movie in data["movies"]:
            assert movie["location"] == "MSK"