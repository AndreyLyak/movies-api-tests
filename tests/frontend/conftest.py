# tests/frontend/conftest.py
import pytest
from playwright.sync_api import sync_playwright
from .tools import Tools  # ← импортируем Tools

DEFAULT_UI_TIMEOUT = 30000


@pytest.fixture(scope="session")
def browser():
    """Запускает браузер один раз для всех тестов"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser):
    """Создаёт новый контекст для каждого теста с записью трассировки"""
    context = browser.new_context()

    # Начинаем запись трассировки
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(DEFAULT_UI_TIMEOUT)

    yield context

    # Останавливаем запись и сохраняем трассировку
    log_name = f"trace_{Tools.get_timestamp()}.zip"
    trace_path = Tools.files_dir('playwright_trace', log_name)
    context.tracing.stop(path=trace_path)
    context.close()


@pytest.fixture(scope="function")
def page(context):
    """Создаёт новую страницу для каждого теста"""
    page = context.new_page()
    yield page
    page.close()

# ========== НОВАЯ ФИКСТУРА С ТЕСТОВЫМИ ДАННЫМИ ==========
@pytest.fixture(scope="session")
def test_user():
    """Фикстура с данными тестового пользователя."""
    return {
        "email": "LyakhovAndreyV@yandex.ru",
        "password": "A11114444",
        "full_name": "Ляхов Андрей Валерьевич"  # Замени, если при регистрации указывал другое
    }
