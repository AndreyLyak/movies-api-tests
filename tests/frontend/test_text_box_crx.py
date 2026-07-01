from playwright.sync_api import Page, expect


def test_text_box_crx(page: Page):
    """Тест: заполнение формы на demoqa.com/text-box (сгенерировано через CRX)"""

    # 1. Переходим на главную
    page.goto("https://demoqa.com/")

    # 2. Кликаем на "Elements"
    page.get_by_role("link", name="Elements").click()

    # 3. Кликаем на "Text Box"
    page.get_by_role("link", name="Text Box").click()

    # 5. Заполняем поля
    page.get_by_role("textbox", name="Full Name").fill("Тестовый Пользователь")
    page.get_by_role("textbox", name="name@example.com").fill("test@example.com")
    page.get_by_role("textbox", name="Current Address").fill("Москва, Красная площадь, 1")
    page.locator("#permanentAddress").fill("Санкт-Петербург, Невский проспект, 2")

    # 6. Нажимаем кнопку Submit
    page.get_by_role("button", name="Submit").click()

    # 7. Проверяем, что появился блок с результатами
    expect(page.locator("#output")).to_be_visible()

    # 8. Проверяем, что данные отобразились корректно
    expect(page.locator("#output #name")).to_have_text("Name:Тестовый Пользователь")
    expect(page.locator("#output #email")).to_have_text("Email:test@example.com")
    expect(page.locator("#output #currentAddress")).to_have_text("Current Address :Москва, Красная площадь, 1")
    expect(page.locator("#output #permanentAddress")).to_have_text(
        "Permananet Address :Санкт-Петербург, Невский проспект, 2")