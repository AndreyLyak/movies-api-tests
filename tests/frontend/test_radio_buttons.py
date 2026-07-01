from playwright.sync_api import Page, expect


def test_radio_buttons(page: Page):
    """Тест: проверка активности радиобатонов на demoqa.com/radio-button"""

    # 1. Переходим на страницу с радиобатонами
    page.goto("https://demoqa.com/radio-button")

    # 2. Проверяем, что радиобатон "Yes" активен
    yes_radio = page.locator("#yesRadio")
    expect(yes_radio).not_to_be_disabled()
    print("✅ Радиобатон 'Yes' активен")

    # 3. Проверяем, что радиобатон "Impressive" активен
    impressive_radio = page.locator("#impressiveRadio")
    expect(impressive_radio).not_to_be_disabled()
    print("✅ Радиобатон 'Impressive' активен")

    # 4. Проверяем, что радиобатон "No" неактивен
    no_radio = page.locator("#noRadio")
    expect(no_radio).to_be_disabled()
    print("✅ Радиобатон 'No' неактивен")

    # 5. Дополнительная проверка: клик по активному радиобатону
    yes_radio.click()
    print("✅ Клик по 'Yes' выполнен")

    # 6. Проверяем, что появился текст с результатом
    result = page.locator(".mt-3")
    expect(result).to_have_text("You have selected Yes")
    print("✅ Текст результата совпадает")