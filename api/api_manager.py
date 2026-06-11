# api/api_manager.py
from clients.movies_client import MoviesAPI
from clients.reviews_client import ReviewsAPI
from clients.user_api import UserApi
from clients.auth_api import AuthAPI  # ← добавь этот импорт


class ApiManager:
    def __init__(self, session):
        self.session = session
        self.movies_api = MoviesAPI(session)
        self.reviews_api = ReviewsAPI(session)
        self.user_api = UserApi(session)
        self.auth_api = AuthAPI(session)  # ← добавь эту строку

    def close_session(self):  # ← добавь этот метод
        """Закрывает HTTP сессию"""
        self.session.close()