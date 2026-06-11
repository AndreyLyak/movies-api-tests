import pytest
from models.user_model import RegisterUserResponse
from enums.roles import Roles


class TestUserAPI:

    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data)
        assert response.status_code == 201

        user_response = RegisterUserResponse(**response.json())

        assert user_response.email == creation_user_data["email"]
        assert user_response.fullName == creation_user_data["fullName"]
        assert user_response.verified is True
        assert user_response.banned is False
        assert Roles.USER.value in user_response.roles
        assert user_response.id is not None

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        create_response = super_admin.api.user_api.create_user(creation_user_data)
        assert create_response.status_code == 201
        created_user = RegisterUserResponse(**create_response.json())

        response_by_id = super_admin.api.user_api.get_user(created_user.id)
        assert response_by_id.status_code == 200
        user_by_id = RegisterUserResponse(**response_by_id.json())

        response_by_email = super_admin.api.user_api.get_user(creation_user_data["email"])
        assert response_by_email.status_code == 200
        user_by_email = RegisterUserResponse(**response_by_email.json())

        assert user_by_id.id == user_by_email.id
        assert user_by_id.email == user_by_email.email
        assert user_by_id.fullName == user_by_email.fullName

    def test_get_user_by_id_common_user(self, common_user):
        response = common_user.api.user_api.get_user(common_user.email, expected_status=403)
        assert response.status_code == 403