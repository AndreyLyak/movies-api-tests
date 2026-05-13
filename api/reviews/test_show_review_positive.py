import requests
import uuid

from constants import BASE_URL, MOVIES_ENDPOINT


def test_show_review(create_movie, auth_token, movie_payload):
    # 1. создаем фильм
    movie_resp = create_movie(movie_payload())

    assert movie_resp.status_code in [200, 201], movie_resp.text
    movie_id = movie_resp.json()["id"]

    headers = {"Authorization": f"Bearer {auth_token}"}

    # 2. создаем отзыв
    review_resp = requests.post(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews",
        json={
            "rating": 5,
            "text": f"Test review {uuid.uuid4()}"
        },
        headers=headers
    )

    assert review_resp.status_code in [200, 201], review_resp.text

    review_data = review_resp.json()
    user_id = review_data["userId"]

    # 3. скрываем отзыв
    hide_resp = requests.patch(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews/hide/{user_id}",
        headers=headers
    )

    assert hide_resp.status_code == 200, hide_resp.text

    # 4. показываем отзыв обратно
    show_resp = requests.patch(
        f"{BASE_URL}{MOVIES_ENDPOINT}/{movie_id}/reviews/show/{user_id}",
        headers=headers
    )

    assert show_resp.status_code == 200, show_resp.text

    data = show_resp.json()

    # 5. проверки
    assert data["userId"] == user_id
    assert "rating" in data
    assert "text" in data
    assert "createdAt" in data