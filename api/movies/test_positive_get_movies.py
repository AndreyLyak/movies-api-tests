import pytest
from pygments.lexers import data


#Проверяем, что апи работает без параметров
#что будет, если я вызову /movies, всё ли работает?
def test_get_movies_default(get_movies):
    response = get_movies()
    assert response.status_code == 200
    data = response.json()
    assert "movies" in data

#Проверяем из сваггера pageSize и page
def test_pagination(get_movies):
    response = get_movies({"page": 2, "pageSize": 5})
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 2
    assert data["pageSize"] == 5

# Фильтр цены
def test_filter_price(get_movies):
    response = get_movies({"minPrice": 100, "maxPrice": 500})
    assert response.status_code == 200
    data = response.json()
    for movie in response.json()["movies"]:
        assert 100 <= movie["price"] <= 500
    assert "movies" in data

@pytest.mark.parametrize("created_at", ["asc", "desc"])
def test_sort(get_movies, created_at):
    response = get_movies({"createdAt": created_at})
    assert response.status_code == 200

    data = response.json()
    assert "movies" in data

#проверка структуры фильма
def test_movie_structure(get_movies):
    response = get_movies()
    data = response.json()
    movie = data["movies"][0]

    assert "id" in movie
    assert "name" in movie
    assert "price" in movie
    assert "location" in movie

#Проверка published
def test_filter_published(get_movies):
    response = get_movies({"published": True})
    data = response.json()

    for movie in data["movies"]:
        assert movie["published"] is True

#Проверка локации
def test_filter_location(get_movies):
    response = get_movies({"location": "MSK"})
    data = response.json()

    if data["movies"]:
        for movie in data["movies"]:
            assert movie["location"] == "MSK"