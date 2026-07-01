from playwright.sync_api import Page, expect
import time


def test_text_box(page: Page):
    """Тест: заполнение формы на demoqa.com/text-box с проверками через expect"""

    # 1. Переходим на страницу
    page.goto('https://demoqa.com/text-box')

    # 2. Заполняем поля
    page.fill('#userName', 'testQa')
    page.fill('#userEmail', 'test@qa.com')
    page.fill('#currentAddress', 'Phuket, Thalang 99')
    page.fill('#permanentAddress', 'Moscow, Mashkova 1')

    # 3. Нажимаем кнопку Submit (уточнённый селектор)
    page.click('button#submit')

    # 4. Ждём появления результата (не обязательно, но для надёжности)
    time.sleep(2)

    # 5. Проверки через expect (Playwright сам будет ждать, пока текст появится)
    expect(page.locator('#output #name')).to_have_text('Name:testQa')
    expect(page.locator('#output #email')).to_have_text('Email:test@qa.com')
    expect(page.locator('#output #currentAddress')).to_have_text('Current Address :Phuket, Thalang 99')
    expect(page.locator('#output #permanentAddress')).to_have_text('Permananet Address :Moscow, Mashkova 1')