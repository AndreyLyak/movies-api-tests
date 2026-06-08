# tests/auth/test_auth_api.py
from models.user_model import RegisterUserResponse
from enums.roles import Roles


class TestAuthAPI:

    def test_register_user(self, super_admin, test_user):
        """Тест регистрации пользователя"""
        user_data = test_user.model_dump(exclude_unset=True)

        response = super_admin.api.user_api.create_user(user_data)
        assert response.status_code == 201

        user_response = RegisterUserResponse(**response.json())

        assert user_response.email == test_user.email
        assert user_response.fullName == test_user.fullName
        assert user_response.verified is False
        assert user_response.banned is False
        assert Roles.USER in user_response.roles

    def test_register_user_invalid_data(self, super_admin):
        """Тест регистрации с невалидными данными"""
        invalid_data = {
            "email": "invalid-email",
            "fullName": "",
            "password": "123",
            "passwordRepeat": "456",
            "roles": ["INVALID_ROLE"]
        }

        response = super_admin.api.user_api.create_user(invalid_data, expected_status=400)
        assert response.status_code == 400