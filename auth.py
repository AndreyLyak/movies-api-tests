import requests

def get_auth_token():
    url = "https://auth.dev-cinescope.coconutqa.ru/login"

    payload = {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

    response = requests.post(url=url, json=payload)

    assert response.status_code == 200

    data = response.json()
    return data["accessToken"]