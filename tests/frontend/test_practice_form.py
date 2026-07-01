from playwright.sync_api import Page, expect


def test_practice_form(page: Page):
    page.goto("https://demoqa.com/automation-practice-form")

    # 1. Заполняем текстовые поля
    page.fill("#firstName", "Тест")
    page.type("#lastName", "Тестов")
    page.fill("#userEmail", "test@example.com")
    page.fill("#userNumber", "1234567890")

    # 2. Выбираем пол (радиобатон)
    page.locator("label[for='gender-radio-1']").click()  # Male

    # 3. Заполняем дату рождения
    date_input = page.locator("#dateOfBirthInput")
    default_date = date_input.get_attribute("value")
    print(f"Дата по умолчанию: {default_date}")
    # (Пока просто выводим, позже добавим проверку)

    # 4. Выбираем предметы (Subjects)
    page.fill("#subjectsInput", "Maths")
    page.keyboard.press("Enter")  # Подтверждаем выбор

    # 5. Выбираем хобби (чекбоксы)
    page.locator("label[for='hobbies-checkbox-1']").click()  # Sports
    page.locator("label[for='hobbies-checkbox-3']").click()  # Music

    # 6. Заполняем адрес
    page.fill("textarea[placeholder='Current Address']", "Москва, Красная площадь, 1")

    # 7. Работаем с выпадающими списками State и City
    page.locator("#state").click()
    page.locator("#react-select-3-option-0").click()  # NCR

    page.locator("#city").click()
    page.locator("#react-select-4-option-0").click()  # Delhi

    print("Форма успешно заполнена!")

    # 8. Нажимаем кнопку Submit
    submit_button = page.locator("#submit")
    submit_button.click()

    # 9. Проверяем, что появилось модальное окно с подтверждением
    # Ищем элемент с текстом "Thanks for submitting the form"
    success_message = page.get_by_text("Thanks for submitting the form")

    # Ждем, пока он станет видимым (это автоматически делает expect)
    expect(success_message).to_be_visible()
    print("✅ Форма успешно отправлена!")