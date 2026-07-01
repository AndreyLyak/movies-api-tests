import time
from playwright.sync_api import sync_playwright
from tests.frontend.models.page_object_models import CinescopRegisterPage


def test_register_by_ui():
    """Тест: регистрация нового пользователя через UI."""

    with sync_playwright() as p:
        # 1. Запускаем браузер
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 2. Создаем объект страницы регистрации
        register_page = CinescopRegisterPage(page)

        # 3. Открываем страницу регистрации
        register_page.open()
        print("✅ Страница регистрации открыта")

        # 4. Заполняем поля по одному (с проверками)
        register_page.enter_full_name("Тест Тестов")
        print("✅ Поле 'ФИО' заполнено")

        register_page.enter_email("test_user_123@email.qa")
        print("✅ Поле 'Email' заполнено")

        register_page.enter_password("Qwerty123!")
        print("✅ Поле 'Пароль' заполнено")

        register_page.enter_repeat_password("Qwerty123!")
        print("✅ Поле 'Повторить пароль' заполнено")

        # 5. Нажимаем кнопку регистрации
        register_page.click_register_button()
        print("✅ Кнопка 'Зарегистрироваться' нажата")

        # 6. Ждем немного, чтобы увидеть результат
        time.sleep(5)

        # 7. Проверяем, что редирект произошел
        register_page.wait_redirect_to_login_page()
        print("✅ Редирект на страницу логина произошел")

        # 8. Проверяем появление и исчезновение алерта
        register_page.check_alert()
        print("✅ Уведомление появилось и исчезло")

        # 9. Пауза для визуальной проверки
        time.sleep(5)

        browser.close()
        print("✅ Тест регистрации пройден успешно!")


if __name__ == "__main__":
    test_register_by_ui()