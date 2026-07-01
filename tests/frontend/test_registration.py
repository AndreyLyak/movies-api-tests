from playwright.sync_api import Page, expect
from random import randint


def test_registration(page: Page):
    """Тест: регистрация нового пользователя с проверкой тостера"""

    # 1. Переходим на страницу регистрации
    page.goto('https://dev-cinescope.coconutqa.ru/register')

    # 2. Локаторы (убедись, что они правильные!)
    username_locator = '[data-qa-id="register_full_name_input"]'
    email_locator = '[data-qa-id="register_email_input"]'
    password_locator = '[data-qa-id="register_password_input"]'
    repeat_password_locator = '[data-qa-id="register_password_repeat_input"]'
    submit_locator = '[data-qa-id="register_submit_button"]'

    # 3. Генерируем уникальный email (рандомное число)
    user_email = f'test_{randint(1, 9999)}@email.qa'

    # 4. Заполняем форму
    page.fill(username_locator, 'Жмышенко Валерий Альбертович')
    page.fill(email_locator, user_email)
    page.fill(password_locator, 'qwerty123Q')
    page.fill(repeat_password_locator, 'qwerty123Q')

    # 5. Нажимаем кнопку регистрации
    page.click(submit_locator)

    # 6. Ждём, пока перебросит на страницу логина
    page.wait_for_url('https://dev-cinescope.coconutqa.ru/login')

    # 7. Проверяем, что появился тостер с текстом
    # Ищем элемент с текстом "Подтвердите свою почту"
    toaster = page.get_by_text("Подтвердите свою почту")

    # Проверяем, что тостер виден на странице
    expect(toaster).to_be_visible()

    # 8. Дополнительная проверка: видим кнопку "Войти" на странице логина
    expect(page.locator('button[type="submit"]')).to_be_visible()

    # 9. Выводим информацию для отладки
    print(f"\n✅ Пользователь {user_email} успешно зарегистрирован!")
    print("✅ Тостер с подтверждением почты появился!")