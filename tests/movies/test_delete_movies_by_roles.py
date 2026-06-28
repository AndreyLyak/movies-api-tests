# tests/movies/test_delete_movies_by_roles.py
import pytest
import allure
import logging
import requests
from constants import BASE_URL, MOVIES_ENDPOINT
from db_requester.movies import MovieDBModel
from db_requester.db_client import SessionLocal

logger = logging.getLogger(__name__)


def get_or_create_movie_in_db(movie_id: int):
    """Получает фильм из БД или создаёт его, если он не существует."""
    session = SessionLocal()
    try:
        movie = session.query(MovieDBModel).filter_by(id=movie_id).first()
        if movie is None:
            logger.warning(f"Фильм с ID {movie_id} не найден в БД. Создаем...")
            from datetime import datetime
            new_movie = MovieDBModel(
                id=movie_id,
                name=f"Тестовый фильм для удаления {movie_id}",
                price=100,
                description="Создан для теста удаления",
                image_url="https://example.com/test.jpg",
                location="SPB",
                published=True,
                rating=5,
                genre_id=1,
                created_at=datetime.now()
            )
            session.add(new_movie)
            session.commit()
            session.refresh(new_movie)
            logger.info(f"Фильм с ID {movie_id} создан в БД")
        else:
            logger.info(f"Фильм с ID {movie_id} найден в БД")
        return movie_id
    except Exception as e:
        logger.error(f"Ошибка при работе с БД: {e}")
        raise
    finally:
        session.close()


def check_movie_deleted_from_db(movie_id: int):
    """Проверяет, что фильм удален из БД."""
    session = SessionLocal()
    try:
        movie = session.query(MovieDBModel).filter_by(id=movie_id).first()
        assert movie is None, f"Фильм с ID {movie_id} остался в БД!"
        logger.info(f"Фильм с ID {movie_id} удален из БД")
    finally:
        session.close()


def check_movie_exists_in_db(movie_id: int):
    """Проверяет, что фильм существует в БД."""
    session = SessionLocal()
    try:
        movie = session.query(MovieDBModel).filter_by(id=movie_id).first()
        assert movie is not None, f"Фильм с ID {movie_id} не найден в БД!"
        logger.info(f"Фильм с ID {movie_id} найден в БД")
    finally:
        session.close()


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_delete_movie_by_super_admin(api_manager, movie_payload, super_admin):
    """SUPER_ADMIN может удалить фильм"""
    with allure.step("Создание фильма через API"):
        create_resp = api_manager.movies_api.create_movie(movie_payload())
        assert create_resp.status_code == 201
        movie_id = create_resp.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Убеждаемся, что фильм есть в БД"):
        get_or_create_movie_in_db(movie_id)

    with allure.step("Удаление фильма через API супер-админом"):
        delete_resp = super_admin.api.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200

    with allure.step("Проверка, что фильм удален из БД"):
        check_movie_deleted_from_db(movie_id)


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_delete_movie_by_admin(api_manager, movie_payload, super_admin, admin_user):
    """ADMIN не может удалить фильм (ожидаем 403)"""
    with allure.step("Создание фильма через API"):
        create_resp = super_admin.api.movies_api.create_movie(movie_payload())
        assert create_resp.status_code == 201
        movie_id = create_resp.json()["id"]

    with allure.step("Убеждаемся, что фильм есть в БД"):
        get_or_create_movie_in_db(movie_id)

    with allure.step("Попытка удалить фильм админом (ожидаем 403)"):
        delete_resp = admin_user.api.movies_api.delete_movie(movie_id, expected_status=403)
        assert delete_resp.status_code == 403

    with allure.step("Проверка, что фильм остался в БД"):
        check_movie_exists_in_db(movie_id)

    with allure.step("Очистка: удаляем фильм супер-админом"):
        super_admin.api.movies_api.delete_movie(movie_id)


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_delete_movie_by_common_user(api_manager, movie_payload, super_admin, common_user):
    """Обычный пользователь (USER) не может удалить фильм (ожидаем 403)"""
    with allure.step("Создание фильма через API"):
        create_resp = super_admin.api.movies_api.create_movie(movie_payload())
        assert create_resp.status_code == 201
        movie_id = create_resp.json()["id"]

    with allure.step("Убеждаемся, что фильм есть в БД"):
        get_or_create_movie_in_db(movie_id)

    with allure.step("Попытка удалить фильм обычным пользователем (ожидаем 403)"):
        delete_resp = common_user.api.movies_api.delete_movie(movie_id, expected_status=403)
        assert delete_resp.status_code == 403

    with allure.step("Проверка, что фильм остался в БД"):
        check_movie_exists_in_db(movie_id)

    with allure.step("Очистка: удаляем фильм супер-админом"):
        super_admin.api.movies_api.delete_movie(movie_id)


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_delete_movie_unauthorized(movie_payload, super_admin):
    """Неавторизованный запрос не может удалить фильм (ожидаем 401)"""
    with allure.step("Создание фильма через API"):
        create_resp = super_admin.api.movies_api.create_movie(movie_payload())
        assert create_resp.status_code == 201
        movie_id = create_resp.json()["id"]

    with allure.step("Убеждаемся, что фильм есть в БД"):
        get_or_create_movie_in_db(movie_id)

    with allure.step("Попытка удалить фильм без авторизации (ожидаем 401)"):
        url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}"
        response = requests.delete(url)
        assert response.status_code == 401

    with allure.step("Проверка, что фильм остался в БД"):
        check_movie_exists_in_db(movie_id)

    with allure.step("Очистка: удаляем фильм супер-админом"):
        super_admin.api.movies_api.delete_movie(movie_id)