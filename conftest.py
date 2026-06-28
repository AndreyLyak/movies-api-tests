import pytest
import requests
import uuid
import random
from datetime import datetime
from auth import get_auth_token
from api.api_manager import ApiManager
import logging
from resources.user_creds import SuperAdminCreds
from enums.roles import Roles
from entities.user import User
from models.user_model import TestUser
from utils.data_generator import DataGenerator
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from typing import Generator
from helpers.db_helper import DBHelper


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

@pytest.fixture(scope="module")
def db_session() -> Generator[Session, None, None]:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper


@pytest.fixture
def test_movie_data():
    """Данные для тестового фильма с уникальным ID"""
    unique_id = random.randint(900000, 999999)

    return {
        "id": unique_id,
        "name": f"Тестовый фильм CRUD {unique_id}",
        "price": 300,
        "description": "Описание для CRUD теста",
        "image_url": "https://example.com/crud_test.jpg",
        "location": "SPB",
        "published": True,
        "rating": 5,
        "genre_id": 1,
        "created_at": datetime.now()
    }


@pytest.fixture
def created_test_movie(db_helper, test_movie_data):
    """
    Фикстура, которая создает тестовый фильм в БД
    и удаляет его после завершения теста
    """
    # Если фильм с таким ID уже есть, удаляем его перед созданием
    if db_helper.movie_exists_by_id(test_movie_data["id"]):
        existing_movie = db_helper.get_movie_by_id(test_movie_data["id"])
        db_helper.delete_movie(existing_movie)
        print(f"🧹 Очистка: удален существующий фильм {test_movie_data['id']}")

    movie = db_helper.create_test_movie(test_movie_data)
    yield movie
    # Cleanup после теста
    if db_helper.movie_exists_by_id(movie.id):
        db_helper.delete_movie(movie)
        print(f"🧹 Очистка: фильм {movie.id} удален")