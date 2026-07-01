from playwright.sync_api import expect, sync_playwright


class GooglePage:
    def __init__(self, page):
        self.page = page
        self.url = "https://www.google.com/"

        # Локаторы элементов
        self.search_input = 'textarea[name="q"]'  # Поле ввода запроса

    def open(self):
        """Открывает страницу Google."""
        self.page.goto(self.url)

    def enter_search_query(self, query):
        """Вводит текст в строку поиска."""
        self.page.fill(self.search_input, query)

    def click_search_button(self):
        """Нажимает Enter для поиска (вместо клика по кнопке)."""
        self.page.keyboard.press("Enter")


def test_google_search():
    """Тест: поиск в Google с проверкой результатов."""

    with sync_playwright() as p:
        # 1. Открываем браузер
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        google_page = GooglePage(page)

        # 2. Открываем Google
        google_page.open()

        # 3. Вводим запрос и ищем (нажатием Enter)
        google_page.enter_search_query("Page Object что это?")
        google_page.click_search_button()

        # 4. Ждем загрузки результатов
        page.wait_for_selector("h3", timeout=10000)

        # 5. Проверяем, что результаты поиска появились
        search_results = page.locator("h3")
        expect(search_results.first).to_be_visible()

        # 6. Проверяем, что в первом результате есть текст "Page Object"
        first_result_text = search_results.first.text_content()
        assert "Page Object" in first_result_text or "page object" in first_result_text, f"Текст 'Page Object' не найден в первом результате. Найден текст: {first_result_text}"

        # 7. Проверяем, что результатов больше одного
        result_count = search_results.count()
        assert result_count > 1, f"Найдено только {result_count} результатов, а ожидалось больше."

        print("✅ Все проверки пройдены успешно!")

        # 8. Закрываем браузер
        browser.close()