from playwright.sync_api import Page, expect


def test_checkbox_tree(page: Page):
    """Тест: проверка видимости и состояния элементов в дереве чекбоксов"""

    # 1. Открываем страницу
    page.goto("https://demoqa.com/checkbox")

    # 2. Проверяем, что "Home" виден
    home_text = page.get_by_text("Home", exact=True)
    expect(home_text).to_be_visible()
    print("✅ 'Home' виден")

    # 3. Проверяем, что "Desktop" НЕ виден
    desktop_text = page.get_by_text("Desktop", exact=True)
    expect(desktop_text).to_be_hidden()
    print("✅ 'Desktop' скрыт")

    # 4. Находим чекбокс "Home" (локатор из DevTools)
    home_checkbox = page.get_by_role("checkbox", name="Select Home")

    # 5. Если чекбокс НЕ выбран — ставим галочку
    if not home_checkbox.is_checked():
        home_checkbox.click()
        print("✅ Чекбокс 'Home' был снят — установили галочку")
    else:
        print("✅ Чекбокс 'Home' уже выбран")

    # 6. Находим и кликаем по стрелке (локатор из DevTools)
    toggle = page.locator(".rc-tree-switcher")
    toggle.click()
    print("✅ Клик по стрелке 'Home' выполнен")

    # 7. Проверяем, что "Desktop" теперь виден
    expect(desktop_text).to_be_visible()
    print("✅ 'Desktop' теперь виден")

    # 8. Проверяем, что чекбокс "Desktop" выбран
    desktop_checkbox = page.get_by_role("checkbox", name="Select Desktop")
    expect(desktop_checkbox).to_be_checked()
    print("✅ Чекбокс 'Desktop' выбран")

    # 9. Снимаем галочку с "Home"
    home_checkbox.click()
    print("✅ Клик по чекбоксу 'Home' (сняли галочку)")

    # 10. Проверяем, что чекбокс "Home" НЕ выбран
    expect(home_checkbox).not_to_be_checked()
    print("✅ Чекбокс 'Home' снят")

    # 11. Проверяем, что чекбокс "Desktop" тоже НЕ выбран
    expect(desktop_checkbox).not_to_be_checked()
    print("✅ Чекбокс 'Desktop' тоже снят")

    print("\n🎉 Все проверки пройдены успешно!")