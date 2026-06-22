# обновленный tests/reviews/test_negative_get_reviews.py
import pytest
import allure
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


@allure.epic("Reviews")
@allure.feature("Получение отзывов")
@allure.story("Негативные сценарии - несуществующий фильм")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_get_reviews_nonexistent_movie(api_manager):
    """Попытка получить отзывы для несуществующего фильма"""

    with allure.step("GET запрос с несуществующим movie_id 99999999"):
        response = api_manager.reviews_api.get_reviews(99999999, expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Reviews")
@allure.feature("Получение отзывов")
@allure.story("Негативные сценарии - невалидный ID")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_get_reviews_invalid_id(api_manager):
    """Попытка получить отзывы с невалидным movie_id (строка)"""

    with allure.step("GET запрос с невалидным movie_id 'abc'"):
        response = api_manager.reviews_api.get_reviews("abc", expected_status=500)

    with allure.step("Проверка статус-кода 500"):
        assert response.status_code == 500, f"Ожидался 500, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Reviews")
@allure.feature("Получение отзывов")
@allure.story("Негативные сценарии - некорректный URL")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_get_reviews_empty_id():
    """Попытка получить отзывы с пустым movie_id (сломанный URL)"""

    with allure.step("GET запрос с некорректным URL (двойной слеш)"):
        url = f"{BASE_URL}{MOVIES_ENDPOINT}//reviews"
        response = requests.get(url)
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка статус-кода (400, 404 или 500)"):
        assert response.status_code in [400, 404, 500], f"Ожидался 400, 404 или 500, получен {response.status_code}"


@allure.epic("Reviews")
@allure.feature("Получение отзывов")
@allure.story("Негативные сценарии - несуществующий фильм")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_get_reviews_large_id(api_manager):
    """Попытка получить отзывы с очень большим movie_id"""

    with allure.step("GET запрос с очень большим movie_id 999999999999"):
        response = api_manager.reviews_api.get_reviews(999999999999, expected_status=500)

    with allure.step("Проверка статус-кода 500"):
        assert response.status_code == 500, f"Ожидался 500, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Reviews")
@allure.feature("Получение отзывов")
@allure.story("Негативные сценарии - неверный метод")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_get_reviews_wrong_method(api_manager):
    """Попытка получить отзывы с использованием POST вместо GET"""

    with allure.step("POST запрос вместо GET"):
        url = f"{BASE_URL}{MOVIES_ENDPOINT}/1/reviews"
        response = requests.post(url, headers=api_manager.session.headers)
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Проверка статус-кода (400, 404 или 405)"):
        assert response.status_code in [400, 404, 405], f"Ожидался 400, 404 или 405, получен {response.status_code}"