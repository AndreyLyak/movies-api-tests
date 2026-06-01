import pytest


def test_negative_pagination(api_manager):
    """Что будет, если отправить неправильную страницу? Ожидаем 400"""
    response = api_manager.movies_api.get_movies(
        params={"page": 0, "pageSize": 20},
        expected_status=400  # ← API возвращает 400
    )

    data = response.json()
    assert "message" in data
    assert "Поле page имеет минимальную величину 1" in data["message"][0]


def test_negative_filter_price(api_manager):
    """Что если minPrice > maxPrice? Ожидаем 400"""
    response = api_manager.movies_api.get_movies(
        params={"minPrice": 0, "maxPrice": -1},
        expected_status=400
    )
    assert response.status_code == 400
    data = response.json()
    assert "message" in data


@pytest.mark.parametrize("created_at", ["up", "down", "123", ""])
def test_negative_sort(api_manager, created_at):
    """Что если передать несуществующую сортировку? Ожидаем 400"""
    response = api_manager.movies_api.get_movies(
        params={"createdAt": created_at},
        expected_status=400
    )
    assert response.status_code == 400
    data = response.json()
    assert "message" in data


@pytest.mark.parametrize("published", ["yes", "no", 123, "null"])
def test_negative_published(api_manager, published):
    """Что если передать не boolean? Ожидаем 400"""
    response = api_manager.movies_api.get_movies(
        params={"published": published},
        expected_status=400
    )
    assert response.status_code == 400
    data = response.json()
    assert "message" in data