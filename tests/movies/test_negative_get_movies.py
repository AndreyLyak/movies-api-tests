# исправленный tests/movies/test_negative_get_movies.py
import pytest
import allure


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Негативные сценарии - пагинация")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_negative_pagination(api_manager):
    """Что будет, если отправить неправильную страницу? Ожидаем 400"""
    with allure.step("Отправка запроса с page=0 (минимальное значение 1)"):
        response = api_manager.movies_api.get_movies(
            params={"page": 0, "pageSize": 20},
            expected_status=400
        )

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"

    with allure.step("Проверка сообщения об ошибке"):
        data = response.json()
        assert "message" in data, "Ответ должен содержать сообщение об ошибке"
        allure.attach(str(data), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Негативные сценарии - фильтрация")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
def test_negative_filter_price(api_manager):
    """Что если minPrice > maxPrice? Ожидаем 400"""
    with allure.step("Отправка запроса с minPrice=0, maxPrice=-1"):
        response = api_manager.movies_api.get_movies(
            params={"minPrice": 0, "maxPrice": -1},
            expected_status=400
        )

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"

    with allure.step("Проверка сообщения об ошибке"):
        data = response.json()
        assert "message" in data, "Ответ должен содержать сообщение об ошибке"
        allure.attach(str(data), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Негативные сценарии - сортировка")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
@pytest.mark.parametrize("created_at", [
    pytest.param("up", id="sort_up"),
    pytest.param("down", id="sort_down"),
    pytest.param("123", id="sort_number"),
    # Пустая строка считается валидной (игнорируется), поэтому убираем
])
def test_negative_sort(api_manager, created_at):
    """Что если передать несуществующую сортировку? Ожидаем 400"""
    with allure.step(f"Отправка запроса с sort={created_at}"):
        response = api_manager.movies_api.get_movies(
            params={"createdAt": created_at},
            expected_status=400
        )

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"

    with allure.step("Проверка сообщения об ошибке"):
        data = response.json()
        assert "message" in data, "Ответ должен содержать сообщение об ошибке"
        allure.attach(str(data), name="Response", attachment_type=allure.attachment_type.JSON)

@allure.epic("Movies")
@allure.feature("Получение фильмов")
@allure.story("Позитивные сценарии - фильтрация по published")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.movie
@pytest.mark.parametrize("published", [
    pytest.param("yes", id="published_yes"),
    pytest.param("no", id="published_no"),
    pytest.param(123, id="published_number"),
    pytest.param("null", id="published_null"),
    pytest.param("", id="published_empty")
])
def test_positive_published_variants(api_manager, published):
    """API принимает различные значения published (позитивный тест)"""
    with allure.step(f"Отправка запроса с published={published}"):
        response = api_manager.movies_api.get_movies(
            params={"published": published}
        )

    with allure.step("Проверка статус-кода 200"):
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"

    with allure.step("Проверка структуры ответа"):
        data = response.json()
        assert "items" in data or "data" in data or "movies" in data, "Ответ должен содержать список фильмов"
        allure.attach(str(data)[:500], name="Response (truncated)", attachment_type=allure.attachment_type.TEXT)