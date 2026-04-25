from constants import MOVIES_ENDPOINT

def test_positive_delete_movie(create_movie, api_client, movie_payload):
    create_response = create_movie(movie_payload())
    assert create_response.status_code in [200, 201]

    movie_id = create_response.json()["id"]

#удаляем
    delete_response = api_client.delete(f"{MOVIES_ENDPOINT}/{movie_id}")
    assert delete_response.status_code == 200

    get_response = api_client.get(f"{MOVIES_ENDPOINT}/{movie_id}")
    assert get_response.status_code == 404