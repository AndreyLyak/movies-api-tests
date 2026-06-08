import json
from models.user_model import UserRegistrationModel


def test_user_model_validation(registration_user_data):
    """
    Проверяем, что registration_user_data проходит валидацию модели.
    """
    print("\n" + "=" * 50)
    print("📝 Обработка registration_user_data")
    print("=" * 50)

    # Валидируем данные через модель
    user_model = UserRegistrationModel(**registration_user_data)

    # Конвертируем в JSON с exclude_unset=False (по умолчанию)
    json_default = user_model.model_dump_json(indent=2)
    print("\n📄 JSON (exclude_unset=False):")
    print(json_default)

    print("\n" + "=" * 50)
    print("📝 Обработка test_user")
    print("=" * 50)


def test_user_model_with_exclude_unset(registration_user_data, test_user):
    """
    Сравниваем вывод с exclude_unset=True и без него.
    """
    # Создаем модель из test_user (у него нет banned и verified)
    user_model = UserRegistrationModel(**test_user)

    print("\n🔍 test_user (исходные данные):")
    print(json.dumps(test_user, indent=2, ensure_ascii=False))

    # JSON без exclude_unset (будут поля со значениями по умолчанию)
    json_with_defaults = user_model.model_dump_json(indent=2)
    print("\n📄 JSON (exclude_unset=False):")
    print(json_with_defaults)

    # JSON с exclude_unset=True (только явно установленные поля)
    json_without_unset = user_model.model_dump_json(indent=2, exclude_unset=True)
    print("\n📄 JSON (exclude_unset=True):")
    print(json_without_unset)

    # Анализ
    print("\n" + "=" * 50)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("=" * 50)

    data_default = json.loads(json_with_defaults)
    data_unset = json.loads(json_without_unset)

    print(f"🔹 exclude_unset=False: присутствуют поля {list(data_default.keys())}")
    print(f"🔹 exclude_unset=True: присутствуют только {list(data_unset.keys())}")

    assert "banned" in data_default, "banned должно быть в JSON с exclude_unset=False"
    assert "banned" not in data_unset, "banned НЕ должно быть в JSON с exclude_unset=True"

    print("\n✅ Тест пройден! Поля со значениями по умолчанию исключаются при exclude_unset=True.")


def test_creation_user_data_validation(creation_user_data):
    """
    Проверяем, что creation_user_data (с banned и verified) валидируется.
    """
    print("\n" + "=" * 50)
    print("📝 Обработка creation_user_data (с banned и verified)")
    print("=" * 50)

    user_model = UserRegistrationModel(**creation_user_data)

    # JSON без exclude_unset (будут видны все поля)
    json_data = user_model.model_dump_json(indent=2)
    print("\n📄 JSON (все поля):")
    print(json_data)

    data = json.loads(json_data)
    assert "banned" in data
    assert "verified" in data
    assert data["banned"] is False
    assert data["verified"] is True

    print("\n✅ creation_user_data содержит banned и verified как и ожидалось.")