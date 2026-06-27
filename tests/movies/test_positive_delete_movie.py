# tests/movies/test_positive_delete_movie.py
import pytest
import allure
import uuid
from db_requester.db_client import SessionLocal
from db_requester.movies import MovieDBModel


def check_movie_exists_in_db(movie_id: int) -> bool:
    """Проверяет, существует ли фильм в БД."""
    session = SessionLocal()
    try:
        movie = session.query(MovieDBModel).filter_by(id=movie_id).first()
        return movie is not None
    finally:
        session.close()


def check_movie_not_exists_in_db(movie_id: int) -> bool:
    """Проверяет, что фильм НЕ существует в БД."""
    session = SessionLocal()
    try:
        movie = session.query(MovieDBModel).filter_by(id=movie_id).first()
        return movie is None
    finally:
        session.close()


@allure.epic("Movies")
@allure.feature("Удаление фильмов")
@allure.story("Позитивные сценарии")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_positive_delete_movie(api_manager, movie_payload):
    """Позитивный тест: удаление фильма"""

    with allure.step("Подготовка данных с уникальным именем"):
        unique_name = f"Delete Test Movie {uuid.uuid4()}"
        payload = movie_payload(name=unique_name)
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(payload)
        assert create_response.status_code == 201, f"Ожидался 201, получен {create_response.status_code}"
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что фильм появился в БД"):
        assert check_movie_exists_in_db(movie_id), f"Фильм с ID {movie_id} не найден в БД!"

    with allure.step("Удаление фильма (ожидаем 200)"):
        delete_response = api_manager.movies_api.delete_movie(movie_id)
        assert delete_response.status_code == 200, f"Ожидался 200, получен {delete_response.status_code}"
        allure.attach(str(delete_response.text), name="Delete Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка, что фильм удален из БД"):
        assert check_movie_not_exists_in_db(movie_id), f"Фильм с ID {movie_id} остался в БД!"
        allure.attach(f"Фильм {movie_id} успешно удален", name="Cleanup", attachment_type=allure.attachment_type.TEXT)