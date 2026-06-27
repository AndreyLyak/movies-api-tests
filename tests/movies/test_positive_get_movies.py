# tests/movies/test_positive_get_movies.py
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


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Позитивные сценарии - структура фильма")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_movie_structure(api_manager, movie_payload):
    """
    Позитивный тест: проверяем структуру фильма.
    Создаём фильм, затем получаем его по ID и проверяем поля.
    """

    with allure.step("Подготовка данных с уникальным именем"):
        unique_name = f"Structure Test {uuid.uuid4()}"
        payload = movie_payload(name=unique_name)
        allure.attach(str(payload), name="Payload", attachment_type=allure.attachment_type.JSON)

    with allure.step("Создание тестового фильма"):
        create_response = api_manager.movies_api.create_movie(payload)
        assert create_response.status_code in [200, 201], f"Ожидался 200 или 201, получен {create_response.status_code}"
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    try:
        with allure.step("Проверка, что фильм появился в БД"):
            assert check_movie_exists_in_db(movie_id), f"Фильм с ID {movie_id} не найден в БД!"
            allure.attach("Фильм успешно создан в БД", name="DB Check", attachment_type=allure.attachment_type.TEXT)

        with allure.step(f"Получение фильма по ID {movie_id}"):
            get_response = api_manager.movies_api.get_movie(movie_id)
            assert get_response.status_code == 200, f"Ожидался 200, получен {get_response.status_code}"
            movie = get_response.json()
            allure.attach(str(movie), name="Movie Data", attachment_type=allure.attachment_type.JSON)

        with allure.step("Проверка структуры фильма (обязательные поля)"):
            required_fields = ["id", "name", "price", "location"]
            for field in required_fields:
                assert field in movie, f"Поле '{field}' отсутствует в структуре фильма"

            allure.attach("Все обязательные поля присутствуют",
                          name="Structure Check",
                          attachment_type=allure.attachment_type.TEXT)

        with allure.step("Проверка корректности данных"):
            assert movie["id"] == movie_id, "ID фильма не совпадает"
            assert movie["name"] == unique_name, "Имя фильма не совпадает"
            assert movie["price"] == payload["price"], "Цена фильма не совпадает"
            assert movie["location"] == payload["location"], "Локация фильма не совпадает"

    finally:
        with allure.step("Очистка: удаление созданного фильма"):
            delete_resp = api_manager.movies_api.delete_movie(movie_id)
            assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
            allure.attach(f"Фильм {movie_id} удален", name="Cleanup",
                          attachment_type=allure.attachment_type.TEXT)
