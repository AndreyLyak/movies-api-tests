# обновленный tests/reviews/test_create_review_negative.py
import pytest
import allure
import requests
from constants import BASE_URL, MOVIES_ENDPOINT


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - авторизация")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.review
def test_update_review_no_auth(api_manager, movie_payload):
    """Попытка обновить отзыв без авторизации"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        assert create_response.status_code == 201
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва для фильма"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201
        user_id = review_response.json().get("userId")
        allure.attach(str(user_id), name="User ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PUT запрос без токена авторизации"):
        url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews"
        response = requests.put(url, json={"rating": 4, "text": "updated"})

    with allure.step("Проверка статус-кода 401"):
        assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - несуществующий фильм")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_not_found(api_manager):
    """Попытка обновить отзыв у несуществующего фильма"""

    with allure.step("PUT запрос с несуществующим movie_id"):
        response = api_manager.reviews_api.update_review(99999999, rating=4, text="test", expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Позитивные сценарии - граничные значения")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_invalid_rating(api_manager, movie_payload):
    """Попытка обновить отзыв с рейтингом больше 5 (API может принять)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва с рейтингом 5"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201

    with allure.step("PUT запрос с рейтингом 10 (API может принять)"):
        response = api_manager.reviews_api.update_review(movie_id, rating=10, text="invalid rating",
                                                         expected_status=200)

    with allure.step("Проверка статус-кода 200"):
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что рейтинг обновился"):
        data = response.json()
        assert data.get("rating") == 10, f"Ожидался рейтинг 10, получен {data.get('rating')}"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Позитивные сценарии - граничные значения")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_negative_rating(api_manager, movie_payload):
    """Попытка обновить отзыв с отрицательным рейтингом (API может принять)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201

    with allure.step("PUT запрос с отрицательным рейтингом"):
        response = api_manager.reviews_api.update_review(movie_id, rating=-1, text="negative rating",
                                                         expected_status=200)

    with allure.step("Проверка статус-кода 200"):
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что рейтинг обновился"):
        data = response.json()
        assert data.get("rating") == -1, f"Ожидался рейтинг -1, получен {data.get('rating')}"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Позитивные сценарии - пустые поля")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_empty_text(api_manager, movie_payload):
    """Попытка обновить отзыв с пустым текстом (API может принять)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201

    with allure.step("PUT запрос с пустым текстом"):
        response = api_manager.reviews_api.update_review(movie_id, rating=4, text="", expected_status=200)

    with allure.step("Проверка статус-кода 200"):
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Проверка, что текст обновился"):
        data = response.json()
        assert data.get("text") == "", f"Ожидался пустой текст, получен {data.get('text')}"

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - отсутствуют поля")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_missing_rating(api_manager, movie_payload):
    """Попытка обновить отзыв без рейтинга (ожидаем 400)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201

    with allure.step("PUT запрос без рейтинга (ожидаем 400)"):
        response = api_manager.reviews_api.update_review(movie_id, text="no rating", expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - отсутствуют поля")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_missing_text(api_manager, movie_payload):
    """Попытка обновить отзыв без текста (ожидаем 400)"""

    with allure.step("Создание фильма через API"):
        create_response = api_manager.movies_api.create_movie(movie_payload())
        movie_id = create_response.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Создание отзыва"):
        review_response = api_manager.reviews_api.create_review(movie_id, rating=5, text="Initial review")
        assert review_response.status_code == 201

    with allure.step("PUT запрос без текста (ожидаем 400)"):
        response = api_manager.reviews_api.update_review(movie_id, rating=3, expected_status=400)

    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - невалидный ID")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_invalid_movie_id(api_manager):
    """Попытка обновить отзыв с невалидным movie_id"""

    with allure.step("PUT запрос с невалидным movie_id 'abc'"):
        response = api_manager.reviews_api.update_review("abc", rating=4, text="test", expected_status=404)

    with allure.step("Проверка статус-кода (400 или 404)"):
        assert response.status_code in [400, 404], f"Ожидался 400 или 404, получен {response.status_code}"
        allure.attach(str(response.text), name="Response", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Reviews")
@allure.feature("Обновление отзывов")
@allure.story("Негативные сценарии - отсутствует отзыв")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
@pytest.mark.api
@pytest.mark.review
def test_update_review_no_review_exists(api_manager, movie_payload):
    """Попытка обновить отзыв, которого не существует"""

    with allure.step("Создание фильма через API"):
        movie_resp = api_manager.movies_api.create_movie(movie_payload())
        movie_id = movie_resp.json()["id"]
        allure.attach(str(movie_id), name="Movie ID", attachment_type=allure.attachment_type.TEXT)

    with allure.step("PUT запрос без создания отзыва (ожидаем 404)"):
        response = api_manager.reviews_api.update_review(movie_id, rating=4, text="no review", expected_status=404)

    with allure.step("Проверка статус-кода 404"):
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
        allure.attach(str(response.json()), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Очистка: удаление фильма"):
        api_manager.movies_api.delete_movie(movie_id)