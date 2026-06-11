from custom_requester.custom_requester import CustomRequester


class UserApi(CustomRequester):
    USER_BASE_URL = "https://auth.dev-cinescope.coconutqa.ru/"

    def __init__(self, session):
        self.session = session
        super().__init__(session, self.USER_BASE_URL)

    def get_user(self, user_locator, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"user/{user_locator}",
            expected_status=expected_status
        )

    def create_user(self, user_data, expected_status=201):
        """Создание пользователя. Принимает словарь или Pydantic модель."""
        if hasattr(user_data, 'model_dump'):
            data = user_data.model_dump(exclude_unset=True)
        else:
            data = user_data

        return self.send_request(
            method="POST",
            endpoint="user",
            data=data,
            expected_status=expected_status
        )