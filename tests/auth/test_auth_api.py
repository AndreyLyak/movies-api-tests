from models.user_model import RegisterUserResponse
from enums.roles import Roles


class TestAuthAPI:

    def test_register_user(self, super_admin, full_registration_user_data):
        response = super_admin.api.user_api.create_user(full_registration_user_data)
        assert response.status_code == 201

        user_response = RegisterUserResponse(**response.json())

        assert user_response.email == full_registration_user_data["email"]
        assert user_response.fullName == full_registration_user_data["fullName"]
        assert user_response.verified is True
        assert user_response.banned is False
        assert Roles.USER.value in user_response.roles

    def test_register_user_invalid_data(self, super_admin):
        invalid_data = {
            "email": "invalid-email",
            "fullName": "",
            "password": "123",
            "passwordRepeat": "456",
            "roles": ["INVALID_ROLE"]
        }

        response = super_admin.api.user_api.create_user(invalid_data, expected_status=400)
        assert response.status_code == 400