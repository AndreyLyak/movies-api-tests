import pytest
import requests
import uuid
from auth import get_auth_token
from constants import BASE_URL, MOVIES_ENDPOINT
from api.api_manager import ApiManager

@pytest.fixture
def auth_token():
    """Возвращает токен авторизации для API запросов"""
    return get_auth_token()


@pytest.fixture
def api_client(auth_token):
    """Клиент для авторизованных запросов к API"""

    class APIClient:
        def __init__(self, token):
            self.headers = {"Authorization": f"Bearer {token}"}
            self.base_url = BASE_URL

        def get(self, endpoint, params=None):
            return requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params
            )

        def post(self, endpoint, json=None):
            return requests.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=json
            )

        def put(self, endpoint, json=None):
            return requests.put(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=json
            )

        def patch(self, endpoint, json=None):
            return requests.patch(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=json
            )

        def delete(self, endpoint, params=None):
            return requests.delete(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params
            )

    return APIClient(auth_token)


@pytest.fixture
def get_movies():
    """Фикстура для получения списка фильмов с возможностью фильтрации"""

    def _get_movies(params=None):
        response = requests.get(
            f"{BASE_URL}{MOVIES_ENDPOINT}",
            params=params
        )
        return response

    return _get_movies


@pytest.fixture
def create_movie(api_client):  # ← изменил зависимость
    """Фикстура для создания фильма"""

    def _create_movie(payload):
        response = api_client.post(  # ← используем api_client
            MOVIES_ENDPOINT,
            json=payload
        )
        return response

    return _create_movie


@pytest.fixture
def movie_payload():
    """
    Фикстура для создания payload фильма с значениями по умолчанию.

    Примеры использования:
        # Стандартный фильм
        payload = movie_payload()

        # Фильм с переопределенными полями
        payload = movie_payload(name="Custom name", price=200)

        # Для негативных тестов
        payload = movie_payload(price=-100, published="invalid")
    """

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


@pytest.fixture
def update_movie(api_client):
    """Фикстура для обновления фильма"""

    def _update_movie(movie_id, **updates):
        response = api_client.patch(
            f"{MOVIES_ENDPOINT}/{movie_id}",
            json=updates
        )
        return response

    return _update_movie


# Дополнительные полезные фикстуры для работы с отзывами
@pytest.fixture
def create_review(api_client):
    """Фикстура для создания отзыва"""

    def _create_review(movie_id, rating=5, text=None):
        if text is None:
            text = f"Test review {uuid.uuid4()}"

        response = api_client.post(
            f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            json={"rating": rating, "text": text}
        )
        return response

    return _create_review


@pytest.fixture
def get_movie(api_client):
    """Фикстура для получения фильма по ID"""

    def _get_movie(movie_id):
        response = api_client.get(f"{MOVIES_ENDPOINT}/{movie_id}")
        return response

    return _get_movie


@pytest.fixture
def delete_movie(api_client):
    """Фикстура для удаления фильма"""

    def _delete_movie(movie_id):
        response = api_client.delete(f"{MOVIES_ENDPOINT}/{movie_id}")
        return response

    return _delete_movie


@pytest.fixture
def get_reviews(api_client):
    """Фикстура для получения отзывов фильма"""

    def _get_reviews(movie_id):
        response = api_client.get(f"{MOVIES_ENDPOINT}/{movie_id}/reviews")
        return response

    return _get_reviews


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


# Добавь эти фикстуры в конец conftest.py

@pytest.fixture
def update_review(api_client):
    """Фикстура для обновления отзыва (PUT)"""

    def _update_review(movie_id, rating=None, text=None):
        payload = {}
        if rating is not None:
            payload["rating"] = rating
        if text is not None:
            payload["text"] = text

        response = api_client.put(
            f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            json=payload
        )
        return response

    return _update_review


@pytest.fixture
def delete_review(api_client):
    """Фикстура для удаления отзыва"""

    def _delete_review(movie_id, user_id=None):
        params = {"userId": user_id} if user_id else {}
        response = api_client.delete(
            f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            params=params
        )
        return response

    return _delete_review


@pytest.fixture
def hide_review(api_client):
    """Фикстура для скрытия отзыва"""

    def _hide_review(movie_id, user_id):
        response = api_client.patch(
            f"{MOVIES_ENDPOINT}/{movie_id}/reviews/hide/{user_id}"
        )
        return response

    return _hide_review


@pytest.fixture
def show_review(api_client):
    """Фикстура для показа отзыва"""

    def _show_review(movie_id, user_id):
        response = api_client.patch(
            f"{MOVIES_ENDPOINT}/{movie_id}/reviews/show/{user_id}"
        )
        return response

    return _show_review

@pytest.fixture(scope="session")
def session():

    http_session = requests.Session()
    token = get_auth_token()
    http_session.headers.update({
        "Authorization": f"Bearer {token}"
    })
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):

    return ApiManager(session)