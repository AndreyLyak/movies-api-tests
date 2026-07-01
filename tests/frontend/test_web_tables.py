from playwright.sync_api import Page, expect


def test_web_tables(page: Page):
    """Тест: работа с таблицей на demoqa.com/webtables"""

    # 1. Переходим на страницу
    page.goto("https://demoqa.com/webtables")

    # 2. Нажимаем кнопку "Add". Находим по роли и тексту
    add_button = page.get_by_role("button", name="Add")
    add_button.click()

    # 3. Проверяем, что форма открылась. Найдём его по заголовку.
    registration_form = page.get_by_text("Registration Form")
    expect(registration_form).to_be_visible()

    # 4. Заполняем поля формы
    page.fill("input[placeholder='First Name']", "Тест")
    page.fill("input[placeholder='Last Name']", "Тестов")
    page.fill("input[placeholder='name@example.com']", "test@example.com")
    page.fill("input[placeholder='Age']", "30")
    page.fill("input[placeholder='Salary']", "50000")
    page.fill("input[placeholder='Department']", "QA")

    # 5. Нажимаем кнопку Submit
    submit_button = page.get_by_role("button", name="Submit")
    submit_button.click()

    # 6. Проверяем, что запись появилась в таблице
    new_row = page.get_by_role("row", name="Тест Тестов 30 test@example.com 50000 QA")
    expect(new_row).to_be_visible()

