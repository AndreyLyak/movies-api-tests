import requests
from constants import BASE_URL, MOVIES_ENDPOINT

def test_get_movie_by_id(create_movie, api_client, movie_payload):

    # сначала создаём фильм
    payload = movie_payload()
    create_response = create_movie(payload)
    assert create_response.status_code in [200, 201]
    movie_id = create_response.json()["id"]

    # потом получаем его
    get_response = requests.get(f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}")

    assert get_response.status_code == 200

    data = get_response.json()
    assert data["id"] == movie_id
    assert data["name"] == payload["name"]