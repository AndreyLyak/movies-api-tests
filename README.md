# Movies API Tests

Автоматизированные тесты для API эндпоинта `/movies`.

## Структура проекта

- **`tests/`** — все тесты  
  - Позитивные тесты имеют в названии с `_positive_...`
  - Негативные тесты имеют в названии `test_negative_...`
- **`conftest.py`** — все фикстуры
- **`constants.py`** — константы, базовые URL, тестовые данные
- **`auth.py`** — функции работы с авторизацией
- **`requirements.txt`** — зависимости

## Как запустить тесты

```bash
# 1. Клонировать репозиторий
git clone https://github.com/AndreyLyak/movies-api-tests.git
cd movies-api-tests

# 2. Создать и активировать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить все тесты
pytest

# Запуск с подробным выводом
pytest -v
