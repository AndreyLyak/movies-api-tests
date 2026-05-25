# test_negative_get_reviews.py
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


# 1. Несуществующий фильм
def test_get_reviews_nonexistent_movie(api_manager):
    response = api_manager.reviews_api.get_reviews(99999999)
    assert response.status_code in [400, 404, 500]


# 2. Невалидный movieId (строка)
def test_get_reviews_invalid_id(api_manager):
    response = api_manager.reviews_api.get_reviews("abc")
    assert response.status_code in [400, 404, 500]


# 3. Пустой movieId (сломанный URL)
def test_get_reviews_empty_id():
    # Для сломанного URL используем прямой запрос, т.к. api_manager может нормализовать URL
    url = f"{BASE_URL}{MOVIES_ENDPOINT}//reviews"
    response = requests.get(url)
    assert response.status_code in [400, 404, 500]


# 4. Очень большой movieId
def test_get_reviews_large_id(api_manager):
    response = api_manager.reviews_api.get_reviews(999999999999)
    assert response.status_code in [400, 404, 500]


# 5. Негатив на метод (POST вместо GET)
def test_get_reviews_wrong_method(api_manager):
    # POST вместо GET — используем прямой запрос или api_manager.post
    # Так как у reviews_api нет метода post для этого эндпоинта, используем прямой запрос
    import requests
    url = f"{BASE_URL}{MOVIES_ENDPOINT}/1/reviews"
    response = requests.post(url, headers=api_manager.session.headers)
    assert response.status_code in [400, 404, 405]