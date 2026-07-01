from playwright.sync_api import Page, expect


def test_dynamic_element(page: Page):
    """Тест: проверка появления элемента 'Visible After 5 Seconds'"""

    # 1. Переходим на страницу
    page.goto("https://demoqa.com/dynamic-properties")

    # 2. Убеждаемся, что элемент отсутствует в первые секунды
    # Используем id="visibleAfter" как локатор
    hidden_element = page.locator("#visibleAfter")

    # Проверяем, что элемента НЕТ на странице сразу после загрузки
    expect(hidden_element).to_be_hidden()
    print("✅ Элемент 'Visible After 5 Seconds' скрыт сразу после загрузки.")

    # 3. Ждем появления элемента с помощью wait_for_selector
    page.wait_for_selector("#visibleAfter", state="visible", timeout=10000)
    print("✅ Элемент 'Visible After 5 Seconds' появился на странице.")

    # 4. Дополнительная проверка: убеждаемся, что элемент теперь виден
    expect(hidden_element).to_be_visible()
    print("✅ Элемент 'Visible After 5 Seconds' теперь видим.")

    print("\n🎉 Тест пройден!")