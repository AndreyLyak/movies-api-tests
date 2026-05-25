import pytest


# Проверяем, что апи работает без параметров
def test_get_movies_default(api_manager):
    response = api_manager.movies_api.get_movies()
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data


# Проверяем из сваггера pageSize и page
def test_pagination(api_manager):
    response = api_manager.movies_api.get_movies(params={"page": 2, "pageSize": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["pageSize"] == 5


# Фильтр цены
def test_filter_price(api_manager):
    response = api_manager.movies_api.get_movies(params={"minPrice": 100, "maxPrice": 500})
    assert response.status_code == 200
    data = response.json()
    for movie in data["movies"]:
        assert 100 <= movie["price"] <= 500
    assert "movies" in data


@pytest.mark.parametrize("created_at", ["asc", "desc"])
def test_sort(api_manager, created_at):
    response = api_manager.movies_api.get_movies(params={"createdAt": created_at})
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data


# проверка структуры фильма
def test_movie_structure(api_manager):
    response = api_manager.movies_api.get_movies()
    data = response.json()
    movie = data["movies"][0]
    assert "id" in movie
    assert "name" in movie
    assert "price" in movie
    assert "location" in movie


# Проверка published
def test_filter_published(api_manager):
    response = api_manager.movies_api.get_movies(params={"published": True})
    data = response.json()
    for movie in data["movies"]:
        assert movie["published"] is True


# Проверка локации
def test_filter_location(api_manager):
    response = api_manager.movies_api.get_movies(params={"location": "MSK"})
    data = response.json()
    if data["movies"]:
        for movie in data["movies"]:
            assert movie["location"] == "MSK"