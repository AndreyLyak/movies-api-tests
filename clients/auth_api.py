# clients/auth_api.py
from custom_requester.custom_requester import CustomRequester


class AuthAPI(CustomRequester):
    AUTH_BASE_URL = "https://auth.dev-cinescope.coconutqa.ru/"

    def __init__(self, session):
        self.session = session
        super().__init__(session, self.AUTH_BASE_URL)

    def login_user(self, login_data, expected_status=201):
        """Авторизация пользователя"""
        return self.send_request(
            method="POST",
            endpoint="login",
            data=login_data,
            expected_status=expected_status
        )

    def authenticate(self, user_creds):
        """Аутентифицирует пользователя и обновляет заголовки сессии"""
        email, password = user_creds
        login_data = {
            "email": email,
            "password": password
        }

        response = self.login_user(login_data).json()
        if "accessToken" not in response:
            raise KeyError("token is missing")

        token = response["accessToken"]
        self._update_session_headers(**{"Authorization": f"Bearer {token}"})