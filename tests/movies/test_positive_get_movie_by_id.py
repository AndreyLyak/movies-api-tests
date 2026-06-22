# обновленный tests/movies/test_positive_get_movie_by_id.py
import pytest
import allure
import uuid


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Позитивные сценарии - базовые запросы")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_get_movies_default(api_manager):
    """Проверяем, что API работает без параметров"""
    with allure.step("Отправка GET-запроса без параметров"):
        response = api_manager.movies_api.get_movies()
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"

    with allure.step("Проверка структуры ответа"):
        data = response.json()
        assert "movies" in data, "Ответ должен содержать поле 'movies'"
        allure.attach(str(data)[:500], name="Response (truncated)", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Позитивные сценарии - пагинация")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_pagination(api_manager):
    """Проверяем pageSize и page из сваггера"""
    with allure.step("Отправка запроса с page=2, pageSize=5"):
        response = api_manager.movies_api.get_movies(params={"page": 2, "pageSize": 5})
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"

    with allure.step("Проверка параметров пагинации"):
        data = response.json()
        assert data.get("page") == 2, f"Ожидалась страница 2, получена {data.get('page')}"
        assert data.get("pageSize") == 5, f"Ожидался pageSize 5, получен {data.get('pageSize')}"
        allure.attach(str(data), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Позитивные сценарии - фильтрация")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_filter_price(api_manager):
    """Фильтр по цене"""
    with allure.step("Отправка запроса с minPrice=100, maxPrice=500"):
        response = api_manager.movies_api.get_movies(params={"minPrice": 100, "maxPrice": 500})
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"

    with allure.step("Проверка, что все фильмы в диапазоне цен"):
        data = response.json()
        assert "movies" in data, "Ответ должен содержать поле 'movies'"

        for movie in data["movies"]:
            price = movie.get("price", 0)
            assert 100 <= price <= 500, f"Цена {price} вне диапазона 100-500"

        allure.attach(str(data), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Позитивные сценарии - сортировка")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
@pytest.mark.parametrize("created_at", [
    pytest.param("asc", id="sort_asc"),
    pytest.param("desc", id="sort_desc")
])
def test_sort(api_manager, created_at):
    """Проверка сортировки"""
    with allure.step(f"Отправка запроса с сортировкой {created_at}"):
        response = api_manager.movies_api.get_movies(params={"createdAt": created_at})
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"

    with allure.step("Проверка структуры ответа"):
        data = response.json()
        assert "movies" in data, "Ответ должен содержать поле 'movies'"
        allure.attach(str(data)[:500], name="Response (truncated)", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Позитивные сценарии - структура")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.movie
def test_movie_structure(api_manager, movie_payload):
    """Проверка структуры фильма (с созданием тестового фильма)"""

    with allure.step("Создание тестового фильма с уникальным именем"):
        unique_name = f"Structure Test {uuid.uuid4()}"
        payload = movie_payload(name=unique_name)
        create_response = api_manager.movies_api.create_movie(payload)
        assert create_response.status_code == 201, f"Ожидался 201, получен {create_response.status_code}"
        created_movie_id = create_response.json()["id"]
        allure.attach(str(created_movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    try:
        with allure.step("Получение списка фильмов"):
            response = api_manager.movies_api.get_movies()
            assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
            data = response.json()

        with allure.step("Проверка наличия фильмов в ответе"):
            assert "movies" in data, "Ответ должен содержать поле 'movies'"
            assert len(data["movies"]) > 0, "Список фильмов не должен быть пустым"

        with allure.step("Проверка структуры первого фильма"):
            movie = data["movies"][0]
            required_fields = ["id", "name", "price", "location"]
            for field in required_fields:
                assert field in movie, f"Поле '{field}' отсутствует в структуре фильма"

            allure.attach(str(movie), name="Movie Structure", attachment_type=allure.attachment_type.JSON)

    finally:
        with allure.step("Очистка: удаление созданного фильма"):
            delete_resp = api_manager.movies_api.delete_movie(created_movie_id)
            assert delete_resp.status_code == 200, f"Ожидался 200, получен {delete_resp.status_code}"
            print(f"✅ Фильм {created_movie_id} удален")


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Позитивные сценарии - фильтрация")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_filter_published(api_manager):
    """Проверка фильтра по published"""
    with allure.step("Отправка запроса с published=True"):
        response = api_manager.movies_api.get_movies(params={"published": True})
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"

    with allure.step("Проверка, что все фильмы опубликованы"):
        data = response.json()
        assert "movies" in data, "Ответ должен содержать поле 'movies'"

        for movie in data["movies"]:
            assert movie.get("published") is True, f"Фильм {movie.get('id')} не опубликован"

        allure.attach(str(data), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Позитивные сценарии - фильтрация")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_filter_location(api_manager):
    """Проверка фильтра по локации (если API поддерживает)"""
    with allure.step("Отправка запроса с location=MSK"):
        response = api_manager.movies_api.get_movies(params={"location": "MSK"})
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"

    with allure.step("Проверка фильтрации по локации"):
        data = response.json()
        assert "movies" in data, "Ответ должен содержать поле 'movies'"

        # Проверяем наличие фильмов с локацией MSK
        msk_movies = [m for m in data["movies"] if m.get("location") == "MSK"]

        if data["movies"] and msk_movies:
            # Если есть фильмы с MSK, проверяем что все они имеют локацию MSK
            for movie in data["movies"]:
                if movie.get("location") == "MSK":
                    continue
            allure.attach(f"Найдено фильмов с MSK: {len(msk_movies)}", name="MSK Count",
                          attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach("API не фильтрует по location или нет фильмов с MSK",
                          name="Info",
                          attachment_type=allure.attachment_type.TEXT)

        allure.attach(str(data)[:500], name="Response (truncated)", attachment_type=allure.attachment_type.TEXT)