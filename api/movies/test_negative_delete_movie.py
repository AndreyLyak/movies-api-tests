# test_negative_delete_movie.py (с дополнительными фикстурами)
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_delete_without_auth(create_movie, get_movie, movie_payload):
    # создаем фильм
    create_response = create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    # проверяем что фильм существует
    assert get_movie(movie_id).status_code == 200

    # DELETE без токена
    url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}"
    delete_response = requests.delete(url)
    assert delete_response.status_code in [401, 403]


def test_delete_nonexistent_movie(delete_movie):
    response = delete_movie(999999999)
    assert response.status_code == 404


def test_delete_invalid_id(delete_movie):
    response = delete_movie("abc")
    assert response.status_code == 404


def test_double_delete_movie(create_movie, delete_movie, movie_payload):
    # создаем фильм
    create_response = create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    # удаляем первый раз
    assert delete_movie(movie_id).status_code == 200

    # удаляем второй раз
    assert delete_movie(movie_id).status_code == 404


def test_delete_then_get_movie(create_movie, delete_movie, get_movie, movie_payload):
    # создаем фильм
    create_response = create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    # проверяем что фильм есть
    assert get_movie(movie_id).status_code == 200

    # удаляем
    assert delete_movie(movie_id).status_code == 200

    # проверяем что фильм исчез
    assert get_movie(movie_id).status_code == 404