# page_object_models
from playwright.sync_api import Page


class CinescopRegisterPage:
    """Page Object для страницы регистрации Cinescope"""

    def __init__(self, page: Page):
        self.page = page
        self.url = "https://dev-cinescope.coconutqa.ru/register"

        # Локаторы элементов (найдены через DevTools)
        self.home_button = "a[href='/' and text()='Cinescope']"
        self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"

        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"

        self.register_button = "button[data-qa-id='register_submit_button']"
        self.sign_button = "a[href='/login' and text()='Войти']"

    # ========== Шапка страницы ==========
    def go_to_home_page(self):
        """Переход на главную страницу."""
        self.page.click(self.home_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/")

    def go_to_all_movies(self):
        """Переход на страницу 'Все фильмы'."""
        self.page.click(self.all_movies_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")

    # ========== Тело страницы ==========
    def open(self):
        """Переход на страницу регистрации."""
        self.page.goto(self.url)

    def enter_full_name(self, full_name: str):
        """Ввод полного имени."""
        self.page.fill(self.full_name_input, full_name)

    def enter_email(self, email: str):
        """Ввод email."""
        self.page.fill(self.email_input, email)

    def enter_password(self, password: str):
        """Ввод пароля."""
        self.page.fill(self.password_input, password)

    def enter_repeat_password(self, password: str):
        """Ввод подтверждения пароля."""
        self.page.fill(self.repeat_password_input, password)

    def click_register_button(self):
        """Клик по кнопке регистрации."""
        self.page.click(self.register_button)

    # ========== Вспомогательные action-методы ==========
    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        """Полный процесс регистрации."""
        self.enter_full_name(full_name)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_repeat_password(confirm_password)
        self.click_register_button()

    def wait_redirect_to_login_page(self):
        """Ожидание редиректа на страницу логина."""
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/login")
        assert self.page.url == "https://dev-cinescope.coconutqa.ru/login", "Редирект на страницу логина не произошел"

    def check_alert(self):
        """Проверка всплывающего сообщения после редиректа."""
        # Проверка появления алерта с текстом "Подтвердите свою почту"
        notification_locator = self.page.get_by_text("Подтвердите свою почту")
        notification_locator.wait_for(state="visible")
        assert notification_locator.is_visible(), "Уведомление не появилось"

        # Ожидание исчезновения алерта
        notification_locator.wait_for(state="hidden")
        assert not notification_locator.is_visible(), "Уведомление не исчезло"


class CinescopLoginPage:
    """Page Object для страницы входа Cinescope"""

    def __init__(self, page: Page):
        self.page = page
        self.url = "https://dev-cinescope.coconutqa.ru/login"

        # Локаторы элементов
        self.home_button = "a[href='/' and text()='Cinescope']"
        self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"

        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"

        self.login_button = "button[data-qa-id='login_submit_button']"
        self.register_button = "a[href='/register' and text()='Зарегистрироваться']"

    # ========== Шапка страницы ==========
    def go_to_home_page(self):
        """Переход на главную страницу."""
        self.page.click(self.home_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/")

    def go_to_all_movies(self):
        """Переход на страницу 'Все фильмы'."""
        self.page.click(self.all_movies_button)
        self.page.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")

    # ========== Тело страницы ==========
    def open(self):
        """Переход на страницу входа."""
        self.page.goto(self.url)

    def enter_email(self, email: str):
        """Ввод email."""
        self.page.fill(self.email_input, email)

    def enter_password(self, password: str):
        """Ввод пароля."""
        self.page.fill(self.password_input, password)

    def click_login_button(self):
        """Клик по кнопке входа."""
        self.page.click(self.login_button)

    # ========== Вспомогательные action-методы ==========
    def login(self, email: str, password: str):
        """Полный процесс входа."""
        self.enter_email(email)
        self.enter_password(password)
        self.click_login_button()

    def wait_redirect_to_home_page(self):
        """Проверяет, что авторизация прошла успешно."""
        # Ждём 3 секунды, чтобы страница успела отреагировать
        self.page.wait_for_timeout(3000)

        # Проверяем, что мы на главной странице
        if "dev-cinescope.coconutqa.ru/" in self.page.url:
            print("✅ Редирект на главную страницу произошел")
            return

        # Проверяем, есть ли кнопка "Выйти" (признак авторизации)
        logout_button = self.page.locator("button:has-text('Выйти'), button:has-text('Выход'), a:has-text('Выйти')")
        if logout_button.count() > 0:
            print("✅ Пользователь авторизован (найдена кнопка 'Выйти')")
            return

        # Проверяем, есть ли сообщение об ошибке
        error = self.page.locator("text=Неверный email или пароль, Ошибка, Error, Invalid")
        if error.count() > 0:
            error_text = error.first.text_content()
            self.page.screenshot(path="login_error.png")
            assert False, f"Ошибка авторизации: {error_text}"

        # Если ничего не подошло — делаем скриншот и падаем
        self.page.screenshot(path="login_unknown_state.png")
        assert False, f"Неизвестное состояние. Текущий URL: {self.page.url}"

    def check_alert(self):
        """Проверка всплывающего сообщения после редиректа."""
        notification_locator = self.page.get_by_text("Вы вошли в аккаунт")
        notification_locator.wait_for(state="visible")
        assert notification_locator.is_visible(), "Уведомление не появилось"

        notification_locator.wait_for(state="hidden")
        assert not notification_locator.is_visible(), "Уведомление не исчезло"


class CinescopMoviePage:
    """Page Object для страницы фильма"""

    def __init__(self, page: Page):
        self.page = page
        self.home_url = "https://dev-cinescope.coconutqa.ru/"

        # Локаторы для отзывов
        self.review_input = '[data-qa-id="movie_review_input"]'
        self.rating_button = 'button[role="combobox"]'  # Кнопка для выбора оценки
        self.rating_option = 'option[value="{rating}"]'  # Опция в выпадающем списке
        self.submit_review_button = '[data-qa-id="movie_review_submit_button"]'
        self.reviews_list = ".review-item"
        self.review_author = "h4.text-xl"
        self.review_text = "p.overflow-hidden"

    def open_movie_page(self, movie_id: str):
        """Открывает страницу фильма по ID."""
        self.page.goto(f"{self.home_url}movies/{movie_id}")

    def leave_review(self, text: str, rating: int = 5):
        """Оставляет отзыв с оценкой."""

        # Прокручиваем к форме отзыва
        self.page.locator('[data-qa-id="movie_review_input"]').scroll_into_view_if_needed()

        # 1. Выбираем оценку из выпадающего списка
        # Пробуем разные способы найти кнопку
        try:
            # Способ 1: по роли
            self.page.click('button[role="combobox"]')
        except:
            # Способ 2: по data-qa-id внутри кнопки
            self.page.click('button:has(span[data-qa-id="movie_rating_select"])')

        # Ждем появления списка
        self.page.wait_for_selector(f'option[value="{rating}"]', state="visible", timeout=5000)

        # Выбираем нужную оценку
        self.page.click(f'option[value="{rating}"]')

        # 2. Вводим текст отзыва
        self.page.fill('[data-qa-id="movie_review_input"]', text)

        # 3. Нажимаем кнопку отправки
        self.page.click('[data-qa-id="movie_review_submit_button"]')

    def get_last_review_text(self) -> str:
        """Получает текст последнего отзыва."""
        reviews = self.page.locator(self.reviews_list)
        if reviews.count() > 0:
            return reviews.last.locator(self.review_text).text_content()
        return ""

    def get_last_review_author(self) -> str:
        """Получает автора последнего отзыва."""
        reviews = self.page.locator(self.reviews_list)
        if reviews.count() > 0:
            return reviews.last.locator(self.review_author).text_content()
        return ""