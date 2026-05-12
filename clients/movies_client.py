from custom_requester.custom_requester import CustomRequester
# from constants import MOVIES_ENDPOINT


class MoviesAPI(CustomRequester):
    """Клиент для работы с фильмами"""

    def __init__(self, session):
        # Базовый URL для API фильмов
        super().__init__(session, base_url="https://api.dev-cinescope.coconutqa.ru")
        self.movies_endpoint = "/movies"

    def create_movie(self, movie_data, expected_status=201):
        """Создать фильм"""
        return self.send_request(
            method="POST",
            endpoint=self.movies_endpoint,
            data=movie_data,
            expected_status=expected_status
        )

    def get_movie(self, movie_id, expected_status=200):
        """Получить фильм по ID"""
        return self.send_request(
            method="GET",
            endpoint=f"{self.movies_endpoint}/{movie_id}",
            expected_status=expected_status
        )

    def get_movies(self, params=None, expected_status=200):
        """Получить список фильмов с фильтрацией"""
        return self.send_request(
            method="GET",
            endpoint=self.movies_endpoint,
            params=params,
            expected_status=expected_status
        )

    def update_movie(self, movie_id, update_data, expected_status=200):
        """Обновить фильм (частично)"""
        return self.send_request(
            method="PATCH",
            endpoint=f"{self.movies_endpoint}/{movie_id}",
            data=update_data,
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        """Удалить фильм"""
        return self.send_request(
            method="DELETE",
            endpoint=f"{self.movies_endpoint}/{movie_id}",
            expected_status=expected_status
        )