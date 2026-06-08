import pytest
from models.user_model import UserRegistrationModel
from enums.roles import Roles


class TestUserValidation:
    """Тесты валидации модели пользователя"""

    # ========== УСПЕШНЫЕ СЛУЧАИ ==========

    @pytest.mark.parametrize("email, password", [
        ("user@example.com", "password123"),
        ("test@gmail.com", "StrongP@ss1"),
        ("valid@mail.ru", "12345678"),
    ])
    def test_valid_user_data(self, email, password):
        """Проверка валидных данных"""
        user_data = {
            "email": email,
            "fullName": "Test User",
            "password": password,
            "passwordRepeat": password,
            "roles": [Roles.USER.value]
        }

        user = UserRegistrationModel(**user_data)
        assert user.email == email
        assert user.password == password
        print(f"\n✅ Валидный пользователь: {user.email}")

    def test_valid_user_from_fixture(self, registration_user_data):
        """Проверка валидных данных из фикстуры"""
        user = UserRegistrationModel(**registration_user_data)
        assert "@" in user.email
        assert len(user.password) >= 8
        print(f"\n✅ Фикстура прошла валидацию: {user.email}")

    # ========== ОШИБКИ ВАЛИДАЦИИ ==========

    @pytest.mark.parametrize("email, error_text", [
        ("usergmail.com", "@"),  # нет @
        ("test@", "@"),  # нет домена
        ("", "@"),  # пустой email
    ])
    def test_invalid_email(self, email, error_text):
        """Проверка невалидного email"""
        user_data = {
            "email": email,
            "fullName": "Test User",
            "password": "password123",
            "passwordRepeat": "password123",
            "roles": [Roles.USER.value]
        }

        with pytest.raises(ValueError) as exc_info:
            UserRegistrationModel(**user_data)

        assert error_text in str(exc_info.value)
        print(f"\n❌ Ожидаемая ошибка: {exc_info.value}")

    @pytest.mark.parametrize("password, length", [
        ("1234567", 7),  # 7 символов
        ("short", 5),  # 5 символов
        ("", 0),  # пустой пароль
    ])
    def test_invalid_password_length(self, password, length):
        """Проверка пароля короче 8 символов"""
        user_data = {
            "email": "test@example.com",
            "fullName": "Test User",
            "password": password,
            "passwordRepeat": password,
            "roles": [Roles.USER.value]
        }

        with pytest.raises(ValueError) as exc_info:
            UserRegistrationModel(**user_data)

        assert "8 символов" in str(exc_info.value)
        print(f"\n❌ Пароль длиной {length} символов: {exc_info.value}")

    def test_password_mismatch(self):
        """Проверка, что пароли не совпадают"""
        user_data = {
            "email": "test@example.com",
            "fullName": "Test User",
            "password": "password123",
            "passwordRepeat": "different456",
            "roles": [Roles.USER.value]
        }

        with pytest.raises(ValueError) as exc_info:
            UserRegistrationModel(**user_data)

        assert "не совпадают" in str(exc_info.value)
        print(f"\n❌ Пароли не совпадают: {exc_info.value}")

    # ========== КОМБИНИРОВАННЫЕ ОШИБКИ ==========

    def test_multiple_validation_errors(self):
        """Проверка нескольких ошибок валидации сразу"""
        user_data = {
            "email": "invalid-email",
            "fullName": "Test User",
            "password": "short",
            "passwordRepeat": "short",
            "roles": [Roles.USER.value]
        }

        with pytest.raises(ValueError) as exc_info:
            UserRegistrationModel(**user_data)

        # Проверяем, что ошибка содержит информацию о проблеме
        error_msg = str(exc_info.value)
        assert ("@" in error_msg or "8 символов" in error_msg)
        print(f"\n❌ Ошибки валидации: {error_msg}")

    # ========== ГЕНЕРАТОР НЕВАЛИДНЫХ ДАННЫХ ==========

    def test_random_invalid_data(self):
        """Генерация и проверка невалидных данных"""
        invalid_cases = [
            {"email": "invalid.com"},
            {"password": "short"},
            {"password": "pass1", "passwordRepeat": "pass2"},
        ]

        for invalid_data in invalid_cases:
            user_data = {
                "email": "test@example.com",
                "fullName": "Test User",
                "password": "password123",
                "passwordRepeat": "password123",
                "roles": [Roles.USER.value],
                **invalid_data
            }

            with pytest.raises(ValueError):
                UserRegistrationModel(**user_data)
                print(f"✅ Поймали ошибку для {list(invalid_data.keys())}")