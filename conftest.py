import pytest
import requests
import uuid
from auth import get_auth_token
from api.api_manager import ApiManager
import logging

# Настройка логирования
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


# ========== Фикстуры для работы с фильмами ==========

@pytest.fixture
def create_movie(api_manager):
    """Создать фильм"""
    def _create_movie(payload):
        response = api_manager.movies_api.create_movie(payload)
        return response
    return _create_movie


@pytest.fixture
def get_movies(api_manager):
    """Получить список фильмов"""
    def _get_movies(params=None):
        response = api_manager.movies_api.get_movies(params=params)
        return response
    return _get_movies


@pytest.fixture
def get_movie(api_manager):
    """Получить фильм по ID"""
    def _get_movie(movie_id):
        response = api_manager.movies_api.get_movie(movie_id)
        return response
    return _get_movie


@pytest.fixture
def update_movie(api_manager):
    """Обновить фильм"""
    def _update_movie(movie_id, **updates):
        response = api_manager.movies_api.update_movie(movie_id, updates)
        return response
    return _update_movie


@pytest.fixture
def delete_movie(api_manager):
    """Удалить фильм"""
    def _delete_movie(movie_id):
        response = api_manager.movies_api.delete_movie(movie_id)
        return response
    return _delete_movie


# ========== Фикстуры для работы с отзывами ==========

@pytest.fixture
def create_review(api_manager):
    """Создать отзыв"""
    def _create_review(movie_id, rating=5, text=None):
        if text is None:
            text = f"Test review {uuid.uuid4()}"
        response = api_manager.reviews_api.create_review(movie_id, rating, text)
        return response
    return _create_review


@pytest.fixture
def get_reviews(api_manager):
    """Получить отзывы фильма"""
    def _get_reviews(movie_id):
        response = api_manager.reviews_api.get_reviews(movie_id)
        return response
    return _get_reviews


@pytest.fixture
def update_review(api_manager):
    """Обновить отзыв"""
    def _update_review(movie_id, rating=None, text=None):
        response = api_manager.reviews_api.update_review(movie_id, rating, text)
        return response
    return _update_review


@pytest.fixture
def delete_review(api_manager):
    """Удалить отзыв"""
    def _delete_review(movie_id, user_id=None):
        response = api_manager.reviews_api.delete_review(movie_id, user_id)
        return response
    return _delete_review


@pytest.fixture
def hide_review(api_manager):
    """Скрыть отзыв"""
    def _hide_review(movie_id, user_id):
        response = api_manager.reviews_api.hide_review(movie_id, user_id)
        return response
    return _hide_review


@pytest.fixture
def show_review(api_manager):
    """Показать отзыв"""
    def _show_review(movie_id, user_id):
        response = api_manager.reviews_api.show_review(movie_id, user_id)
        return response
    return _show_review


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
def create_movie_with_review(create_movie, create_review, movie_payload):
    """Создает фильм с отзывом и возвращает все данные"""
    def _create(movie_overrides=None, review_rating=5, review_text=None):
        # Создаем фильм
        if movie_overrides:
            movie_resp = create_movie(movie_payload(**movie_overrides))
        else:
            movie_resp = create_movie(movie_payload())

        assert movie_resp.status_code in [200, 201]
        movie_data = movie_resp.json()
        movie_id = movie_data["id"]

        # Создаем отзыв
        review_resp = create_review(movie_id, review_rating, review_text)
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


# ========== Фикстура для данных обновления ==========

@pytest.fixture
def update_movie_data(movie_payload):
    """Генерирует данные для обновления фильма"""
    def _update_movie_data(**kwargs):
        default_data = movie_payload(
            name=f"Updated Movie {uuid.uuid4()}",
            description="Updated description",
            price=200,
            location="MSK",
            imageUrl="https://new-image.url",
            published=False
        )
        default_data.update(kwargs)
        # Убираем поля, которые нельзя обновлять
        default_data.pop("id", None)
        return default_data
    return _update_movie_data