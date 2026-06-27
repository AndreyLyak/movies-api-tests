# tests/movies/test_movies_with_roles.py
import pytest
import allure
import logging
from db_requester.db_client import SessionLocal
from db_requester.movies import MovieDBModel

logger = logging.getLogger(__name__)


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_common_user_cannot_create_movie(common_user, movie_payload):
    """Негативный тест: USER не может создать фильм"""
    with allure.step("Подготовка данных для создания фильма"):
        payload = movie_payload()
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Попытка создать фильм пользователем с ролью USER (ожидаем 403)"):
        response = common_user.api.movies_api.create_movie(payload, expected_status=403)
        assert response.status_code == 403

    with allure.step("Проверка, что фильм не был создан"):
        assert "Forbidden" in str(response.text) or response.status_code == 403


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_admin_user_cannot_create_movie(admin_user, movie_payload):
    """Тест: ADMIN не может создать фильм (ожидаем 403)"""
    with allure.step("Подготовка данных для создания фильма"):
        payload = movie_payload()
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Попытка создать фильм пользователем с ролью ADMIN (ожидаем 403)"):
        response = admin_user.api.movies_api.create_movie(payload, expected_status=403)
        assert response.status_code == 403

    with allure.step("Проверка, что фильм не был создан"):
        assert "Forbidden" in str(response.text) or response.status_code == 403


@allure.epic("Movies")
@allure.feature("Создание фильмов")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_super_admin_can_create_movie(super_admin, movie_payload):
    """Позитивный тест: SUPER_ADMIN может создать фильм"""
    with allure.step("Подготовка данных для создания фильма"):
        payload = movie_payload()
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание фильма супер-админом"):
        response = super_admin.api.movies_api.create_movie(payload)
        assert response.status_code == 201

    with allure.step("Получение ID созданного фильма"):
        movie_data = response.json()
        movie_id = movie_data["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка созданного фильма"):
        assert movie_data.get("name") == payload["name"]
        assert movie_data.get("price") == payload["price"]

    with allure.step("Очистка: удаление созданного фильма"):
        delete_resp = super_admin.api.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200
        allure.attach(f"Фильм {movie_id} удален", name="Cleanup", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_common_user_cannot_delete_movie(common_user, super_admin, movie_payload):
    """Негативный тест: USER не может удалить фильм"""
    with allure.step("Создание фильма супер-админом для теста"):
        create_resp = super_admin.api.movies_api.create_movie(movie_payload())
        assert create_resp.status_code == 201
        movie_id = create_resp.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Попытка удалить фильм пользователем с ролью USER (ожидаем 403)"):
        response = common_user.api.movies_api.delete_movie(movie_id, expected_status=403)
        assert response.status_code == 403

    with allure.step("Проверка, что фильм остался в БД"):
        session = SessionLocal()
        try:
            movie = session.query(MovieDBModel).filter_by(id=movie_id).first()
            assert movie is not None, f"Фильм с ID {movie_id} был удален, хотя не должен был!"
        finally:
            session.close()

    with allure.step("Очистка: удаление фильма супер-админом"):
        delete_resp = super_admin.api.movies_api.delete_movie(movie_id)
        assert delete_resp.status_code == 200
        allure.attach(f"Фильм {movie_id} удален", name="Cleanup", attachment_type=allure.attachment_type.TEXT)