import pytest

#что будет, если отправить неправильную страницу?
def test_negative_pagination(get_movies):
    response = get_movies({"page": 0, "pageSize": 20})
    assert response.status_code in [400, 422]

#Что если minPrice > maxPrice или отрицательные значения?
def test_negative_filter_price(get_movies):
    response = get_movies({"minPrice": 0, "maxPrice": -1})
    assert response.status_code in [400, 422]

#Что если передать несуществующую сортировку?
@pytest.mark.parametrize("created_at", ["up", "down", "123", ""])
def test_negative_sort(get_movies, created_at):
    response = get_movies({"createdAt": created_at})
    assert response.status_code in [400, 422]

#Что если передать не boolean?
@pytest.mark.parametrize("published", ["yes", "no", 123, "null"])
def test_negative_published(get_movies, published):
    response = get_movies({"published": published})
    assert response.status_code in [400, 422]

