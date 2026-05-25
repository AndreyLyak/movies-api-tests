import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_delete_without_auth(api_manager, movie_payload):
    # создаем фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    # проверяем что фильм существует
    get_response = api_manager.movies_api.get_movie(movie_id)
    assert get_response.status_code == 200

    # DELETE без токена
    url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}"
    delete_response = requests.delete(url)
    assert delete_response.status_code in [401, 403]


def test_delete_nonexistent_movie(api_manager):
    response = api_manager.movies_api.delete_movie(999999999)
    assert response.status_code == 404


def test_delete_invalid_id(api_manager):
    response = api_manager.movies_api.delete_movie("abc")
    assert response.status_code == 404


def test_double_delete_movie(api_manager, movie_payload):
    # создаем фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    # удаляем первый раз
    assert api_manager.movies_api.delete_movie(movie_id).status_code == 200

    # удаляем второй раз
    assert api_manager.movies_api.delete_movie(movie_id).status_code == 404


def test_delete_then_get_movie(api_manager, movie_payload):
    # создаем фильм
    create_response = api_manager.movies_api.create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    # проверяем что фильм есть
    assert api_manager.movies_api.get_movie(movie_id).status_code == 200

    # удаляем
    assert api_manager.movies_api.delete_movie(movie_id).status_code == 200

    # проверяем что фильм исчез
    assert api_manager.movies_api.get_movie(movie_id).status_code == 404