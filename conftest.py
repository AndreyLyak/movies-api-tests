import pytest
import requests
import uuid
from auth import get_auth_token
from api.api_manager import ApiManager
import logging
from resources.user_creds import SuperAdminCreds
from enums.roles import Roles
from entities.user import User
from models.user_model import TestUser
from utils.data_generator import DataGenerator

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
            "description": "Test description",
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


# ========== ФИКСТУРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========

@pytest.fixture
def test_user() -> TestUser:
    """Генерирует тестовые данные для пользователя с использованием Pydantic модели"""
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )


@pytest.fixture
def user_session():
    """Фикстура для создания сессии пользователя"""
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_api_manager = ApiManager(session)
        user_pool.append(user_api_manager)
        return user_api_manager

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def creation_user_data():
    """Данные для создания пользователя (с verified и banned)"""
    random_password = DataGenerator.generate_random_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value],
        "verified": True,
        "banned": False
    }


@pytest.fixture
def full_registration_user_data():
    """Данные для регистрации пользователя с обязательными полями verified и banned"""
    random_password = DataGenerator.generate_random_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value],
        "verified": False,
        "banned": False
    }


@pytest.fixture
def super_admin(user_session):
    """Фикстура для создания супер-админа"""
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    """Фикстура для создания обычного пользователя с ролью USER"""
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user


@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    """Фикстура для создания пользователя с ролью ADMIN"""
    new_session = user_session()

    admin_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.ADMIN.value],
        new_session)

    user_data = creation_user_data.copy()
    user_data["roles"] = [Roles.ADMIN.value]
    super_admin.api.user_api.create_user(user_data)

    admin_user.api.auth_api.authenticate(admin_user.creds)
    return admin_user