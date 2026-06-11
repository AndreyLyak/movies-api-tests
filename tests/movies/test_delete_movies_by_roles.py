import requests
from constants import BASE_URL, MOVIES_ENDPOINT


def test_delete_movie_by_super_admin(api_manager, movie_payload, super_admin):
    """SUPER_ADMIN может удалить фильм"""
    create_resp = api_manager.movies_api.create_movie(movie_payload())
    assert create_resp.status_code == 201
    movie_id = create_resp.json()["id"]

    delete_resp = super_admin.api.movies_api.delete_movie(movie_id)
    assert delete_resp.status_code == 200

    get_resp = api_manager.movies_api.get_movie(movie_id, expected_status=404)
    assert get_resp.status_code == 404


def test_delete_movie_by_admin(api_manager, movie_payload, super_admin, admin_user):
    """ADMIN не может удалить фильм (ожидаем 403)"""
    create_resp = super_admin.api.movies_api.create_movie(movie_payload())
    assert create_resp.status_code == 201
    movie_id = create_resp.json()["id"]

    delete_resp = admin_user.api.movies_api.delete_movie(movie_id, expected_status=403)
    assert delete_resp.status_code == 403

    super_admin.api.movies_api.delete_movie(movie_id)


def test_delete_movie_by_common_user(api_manager, movie_payload, super_admin, common_user):
    """Обычный пользователь (USER) не может удалить фильм (ожидаем 403)"""
    create_resp = super_admin.api.movies_api.create_movie(movie_payload())
    assert create_resp.status_code == 201
    movie_id = create_resp.json()["id"]

    delete_resp = common_user.api.movies_api.delete_movie(movie_id, expected_status=403)
    assert delete_resp.status_code == 403

    super_admin.api.movies_api.delete_movie(movie_id)


def test_delete_movie_unauthorized(movie_payload, super_admin):
    """Неавторизованный запрос не может удалить фильм (ожидаем 401)"""
    create_resp = super_admin.api.movies_api.create_movie(movie_payload())
    assert create_resp.status_code == 201
    movie_id = create_resp.json()["id"]

    url = f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}"
    response = requests.delete(url)
    assert response.status_code == 401

    super_admin.api.movies_api.delete_movie(movie_id)