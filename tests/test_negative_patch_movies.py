from constants import MOVIES_ENDPOINT


def test_patch_without_auth(create_movie, movie_payload):
    # создаем фильм
    response = create_movie(movie_payload())
    assert response.status_code == 201
    movie_id = response.json()["id"]

    # БЕЗ авторизации - прямой запрос
    import requests
    from constants import BASE_URL

    response = requests.patch(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}",
        json={"name": "Updated without auth"}
    )
    assert response.status_code in [401, 403]


def test_patch_nonexistent_movie(update_movie):
    response = update_movie(99999999, name="Updated")
    assert response.status_code == 404


def test_patch_invalid_id(update_movie):
    response = update_movie("abc", name="Updated")
    assert response.status_code in [400, 404]


def test_patch_invalid_data(create_movie, update_movie, movie_payload):
    create_response = create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    response = update_movie(movie_id, price=-100)
    assert response.status_code in [200, 400]


def test_patch_empty_body(create_movie, update_movie, movie_payload):
    create_response = create_movie(movie_payload())
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]

    response = update_movie(movie_id)  # без параметров = пустой body
    assert response.status_code in [400, 200]