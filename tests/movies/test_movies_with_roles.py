def test_common_user_cannot_create_movie(common_user, movie_payload):
    """Негативный тест: USER не может создать фильм"""
    payload = movie_payload()
    response = common_user.api.movies_api.create_movie(payload, expected_status=403)
    assert response.status_code == 403


def test_admin_user_can_create_movie(admin_user, movie_payload):
    """Тест: ADMIN не может создать фильм (ожидаем 403)"""
    payload = movie_payload()
    response = admin_user.api.movies_api.create_movie(payload, expected_status=403)
    assert response.status_code == 403


def test_super_admin_can_create_movie(super_admin, movie_payload):
    """Позитивный тест: SUPER_ADMIN может создать фильм"""
    payload = movie_payload()
    response = super_admin.api.movies_api.create_movie(payload)
    assert response.status_code == 201
    movie_id = response.json()["id"]
    super_admin.api.movies_api.delete_movie(movie_id)


def test_common_user_cannot_delete_movie(common_user, super_admin, movie_payload):
    """Негативный тест: USER не может удалить фильм"""
    create_resp = super_admin.api.movies_api.create_movie(movie_payload())
    assert create_resp.status_code == 201
    movie_id = create_resp.json()["id"]

    response = common_user.api.movies_api.delete_movie(movie_id, expected_status=403)
    assert response.status_code == 403

    super_admin.api.movies_api.delete_movie(movie_id)