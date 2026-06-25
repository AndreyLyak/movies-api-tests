# tests/auth/test_auth_api.py
import allure
from pytest_check import check
from models.user_model import RegisterUserResponse
from models.error_model import ErrorResponse
from enums.roles import Roles


class TestAuthAPI:

    @allure.title("Тест регистрации пользователя с валидными данными")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Your Name")
    @allure.feature("Авторизация")
    @allure.story("Регистрация пользователя")
    def test_register_user(self, super_admin, full_registration_user_data):
        """Тест регистрации пользователя с проверкой всех полей через soft asserts"""

        with allure.step("Отправка запроса на регистрацию пользователя"):
            response = super_admin.api.user_api.create_user(full_registration_user_data)

        with allure.step("Проверка статус-кода ответа"):
            assert response.status_code == 201, f"Ожидался статус 201, получен {response.status_code}"

        with allure.step("Парсинг ответа в модель RegisterUserResponse"):
            user_response = RegisterUserResponse(**response.json())

        with allure.step("Проверка всех полей пользователя (soft asserts)"):
            with check("Проверка email"):
                check.equal(
                    user_response.email,
                    full_registration_user_data["email"],
                    f"Email не совпадает: ожидался {full_registration_user_data['email']}, получен {user_response.email}"
                )

            with check("Проверка fullName"):
                check.equal(
                    user_response.fullName,
                    full_registration_user_data["fullName"],
                    f"fullName не совпадает: ожидался {full_registration_user_data['fullName']}, получен {user_response.fullName}"
                )

            with check("Проверка verified"):
                check.is_true(
                    user_response.verified,
                    f"verified должен быть True, получен {user_response.verified}"
                )

            with check("Проверка banned"):
                check.is_false(
                    user_response.banned,
                    f"banned должен быть False, получен {user_response.banned}"
                )

            with check("Проверка roles"):
                check.is_true(
                    Roles.USER.value in user_response.roles,
                    f"Роль {Roles.USER.value} не найдена в {user_response.roles}"
                )

    @allure.title("Тест регистрации с невалидными данными")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.feature("Авторизация")
    @allure.story("Регистрация пользователя")
    def test_register_user_invalid_data(self, super_admin):
        """Тест с невалидными данными — проверка ошибок валидации"""

        invalid_data = {
            "email": "invalid-email",
            "fullName": "",
            "password": "123",
            "passwordRepeat": "456",
            "roles": ["INVALID_ROLE"]
        }

        with allure.step("Отправка запроса с невалидными данными"):
            response = super_admin.api.user_api.create_user(invalid_data, expected_status=400)

        with allure.step("Проверка статус-кода ошибки"):
            assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"

        with allure.step("Проверка сообщения об ошибке"):
            error_data = ErrorResponse(**response.json())
            assert error_data.detail or error_data.message, "Ответ должен содержать информацию об ошибке"
            allure.attach(str(error_data.model_dump()), name="Error Response", attachment_type=allure.attachment_type.JSON)
            print(f"✅ Ошибка валидации: {error_data.model_dump()}")