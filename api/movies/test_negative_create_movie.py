def test_create_movie_invalid_price(create_movie, movie_payload):
    """Попытка создать фильм с отрицательной ценой"""
    payload = movie_payload(price=-100)
    response = create_movie(payload)

    assert response.status_code == 400
    assert "error" in response.json() or "message" in response.json()


def test_create_movie_duplicate(create_movie, movie_payload):
    """Попытка создать два фильма с одинаковым именем"""
    fixed_name = "Test Movie Duplicate"
    payload = movie_payload(name=fixed_name)

    response1 = create_movie(payload)
    assert response1.status_code in [201, 409]

    response2 = create_movie(payload)
    assert response2.status_code == 409


def test_create_movie_empty_name(create_movie, movie_payload):
    """Попытка создать фильм с пустым именем"""
    payload = movie_payload(name="")
    response = create_movie(payload)

    assert response.status_code == 400


def test_create_movie_missing_required_field(create_movie, movie_payload):
    """Попытка создать фильм без обязательного поля (например, без name)"""
    payload = movie_payload()
    del payload["name"]  # удаляем обязательное поле

    response = create_movie(payload)
    assert response.status_code == 400


def test_create_movie_invalid_genre(create_movie, movie_payload):
    """Попытка создать фильм с несуществующим жанром"""
    payload = movie_payload(genreId=999)
    response = create_movie(payload)

    assert response.status_code in [400, 404]


def test_create_movie_without_auth(create_movie, movie_payload):
    """Попытка создать фильм без авторизации"""
    # Этот тест требует прямого запроса без токена
    import requests
    from constants import BASE_URL, MOVIES_ENDPOINT

    payload = movie_payload()
    response = requests.post(
        f"{BASE_URL}{MOVIES_ENDPOINT}",
        json=payload
    )
    assert response.status_code == 401