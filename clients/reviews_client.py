from custom_requester.custom_requester import CustomRequester
from constants import MOVIES_ENDPOINT


class ReviewsAPI(CustomRequester):
    """Клиент для работы с отзывами"""

    def __init__(self, session):
        super().__init__(session, base_url="https://api.dev-cinescope.coconutqa.ru")

    def create_review(self, movie_id, rating, text, expected_status=201):
        """Создать отзыв"""
        return self.send_request(
            method="POST",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            data={"rating": rating, "text": text},
            expected_status=expected_status
        )

    def get_reviews(self, movie_id, expected_status=200):
        """Получить все отзывы фильма"""
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            expected_status=expected_status
        )

    def update_review(self, movie_id, rating=None, text=None, expected_status=200):
        """Обновить отзыв (PUT)"""
        data = {}
        if rating is not None:
            data["rating"] = rating
        if text is not None:
            data["text"] = text
        return self.send_request(
            method="PUT",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            data=data,
            expected_status=expected_status
        )

    def delete_review(self, movie_id, user_id=None, expected_status=200):
        """Удалить отзыв"""
        endpoint = f"{MOVIES_ENDPOINT}/{movie_id}/reviews"
        if user_id:
            endpoint = f"{endpoint}?userId={user_id}"
        return self.send_request(
            method="DELETE",
            endpoint=endpoint,
            expected_status=expected_status
        )

    def hide_review(self, movie_id, user_id, expected_status=200):
        """Скрыть отзыв"""
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews/hide/{user_id}",
            expected_status=expected_status
        )

    def show_review(self, movie_id, user_id, expected_status=200):
        """Показать отзыв"""
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews/show/{user_id}",
            expected_status=expected_status
        )