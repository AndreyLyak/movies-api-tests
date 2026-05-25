import pytest
import requests
import uuid
from auth import get_auth_token
from api.api_manager import ApiManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture(scope="session")
def auth_token():
    """Возвращает токен авторизации для API запросов"""
    return get_auth_token()


@pytest.fixture(scope="session")
def session(auth_token):
    """Создает HTTP сессию с токеном авторизации"""
    http_session = requests.Session()
    http_session.headers.update({
        "Authorization": f"Bearer {auth_token}"
    })
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """Возвращает ApiManager для работы с API"""
    return ApiManager(session)


# ========== Фикстура для генерации данных ==========

@pytest.fixture
def movie_payload():
    """Генерирует данные для создания фильма"""

    def _movie_payload(**kwargs):
        default_payload = {
            "name": f"Test movie {uuid.uuid4()}",
            "imageUrl": "https://img.com",
            "price": 100,
            "description": "Test",
            "location": "SPB",
            "published": True,
            "genreId": 1
        }
        default_payload.update(kwargs)
        return default_payload

    return _movie_payload


# ========== Комплексная фикстура ==========

@pytest.fixture
def create_movie_with_review(api_manager, movie_payload):
    """Создает фильм с отзывом и возвращает все данные"""

    def _create(movie_overrides=None, review_rating=5, review_text=None):
        # Создаем фильм
        if movie_overrides:
            movie_resp = api_manager.movies_api.create_movie(movie_payload(**movie_overrides))
        else:
            movie_resp = api_manager.movies_api.create_movie(movie_payload())

        assert movie_resp.status_code in [200, 201]
        movie_data = movie_resp.json()
        movie_id = movie_data["id"]

        # Создаем отзыв
        review_resp = api_manager.reviews_api.create_review(movie_id, review_rating, review_text)
        assert review_resp.status_code in [200, 201]

        review_data = review_resp.json()
        if isinstance(review_data, list):
            review_data = review_data[0]

        return {
            "movie_id": movie_id,
            "movie_data": movie_data,
            "review_data": review_data,
            "user_id": review_data.get("userId")
        }

    return _create