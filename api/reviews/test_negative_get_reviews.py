# test_negative_get_reviews.py
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


# 1. Несуществующий фильм
def test_get_reviews_nonexistent_movie(api_client):
    response = api_client.get(f"{MOVIES_ENDPOINT}/99999999/reviews")
    assert response.status_code in [400, 404, 500]


# 2. Невалидный movieId (строка)
def test_get_reviews_invalid_id(api_client):
    response = api_client.get(f"{MOVIES_ENDPOINT}/abc/reviews")
    assert response.status_code in [400, 404, 500]


# 3. Пустой movieId (сломанный URL)
def test_get_reviews_empty_id():
    # Для сломанного URL используем прямой запрос, т.к. api_client может нормализовать URL
    url = f"{BASE_URL}{MOVIES_ENDPOINT}//reviews"
    response = requests.get(url)
    assert response.status_code in [400, 404, 500]


# 4. Очень большой movieId
def test_get_reviews_large_id(api_client):
    response = api_client.get(f"{MOVIES_ENDPOINT}/999999999999/reviews")
    assert response.status_code in [400, 404, 500]


# 5. Негатив на метод (POST вместо GET)
def test_get_reviews_wrong_method(api_client):
    # POST вместо GET
    response = api_client.post(f"{MOVIES_ENDPOINT}/1/reviews")
    assert response.status_code in [400, 404, 405]