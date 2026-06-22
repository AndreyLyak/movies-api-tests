# auth.py
import requests


def get_auth_token():
    """Получает токен авторизации для API запросов"""
    url = "https://auth.dev-cinescope.coconutqa.ru/login"

    payload = {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

    response = requests.post(url=url, json=payload)

    # Сервер возвращает 201 Created при успешном логине
    assert response.status_code == 201, f"Ожидался 201, получен {response.status_code}"

    token = response.json().get("accessToken")
    assert token is not None, "Токен не найден в ответе"

    return token