# tests/api/test_mock_services.py
import sys
import os
import requests
from datetime import datetime
import pytz
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class WorldClockResponse(BaseModel):
    id: str = Field(alias="$id")
    currentDateTime: str
    utcOffset: str
    isDayLightSavingsTime: bool
    dayOfTheWeek: str
    timeZoneName: str
    currentFileTime: int
    ordinalDate: str
    serviceResponse: None

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True,
    }


class WhatIsTodayResponse(BaseModel):
    message: str


def get_worldclockap_time():
    response = requests.get("http://worldclockapi.com/api/json/utc/now")  # noqa
    assert response.status_code == 200
    return WorldClockResponse(**response.json())


def get_fake_worldclockap_time():
    response = requests.get("http://127.0.0.1:16001/fake/worldclockapi/api/json/utc/now")  # noqa
    assert response.status_code == 200
    return WorldClockResponse(**response.json())


class TestTodayIsHolidayServiceAPI:

    def test_worldclockap(self):
        world_clock_response = get_worldclockap_time()
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время: {current_date_time=}")
        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ")

    def test_what_is_today(self):
        world_clock_response = get_worldclockap_time()
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": world_clock_response.currentDateTime}
        )
        assert what_is_today_response.status_code == 200
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Сегодня нет праздников в России."

    def test_mock_simple(self, mocker):
        """Простой тест для проверки мока"""

        # Патчим
        mocker.patch(
            "tests.api.test_mock_services.get_worldclockap_time",
            return_value="2025-01-01T00:00Z"
        )

        # Вызываем
        result = get_worldclockap_time()

        # Проверяем
        print(f"🔍 result = {result}")
        assert result == "2025-01-01T00:00Z"

    def test_what_is_today_by_mock(self, mocker):
        """Тест с использованием Mock"""

        # Создаем мок-объект
        mock_response = mocker.Mock()
        mock_response.currentDateTime = "2025-01-01T00:00Z"

        # ПАТЧИМ ДО ВЫЗОВА!
        mocker.patch(
            "tests.api.test_mock_services.get_worldclockap_time",
            return_value=mock_response
        )

        # ТЕПЕРЬ вызываем — должен вернуться мок
        world_clock_response = get_worldclockap_time()

        print(f"\n🔍 DEBUG: world_clock_response.currentDateTime = {world_clock_response.currentDateTime}")

        # Отправляем запрос
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": world_clock_response.currentDateTime}
        )

        print(f"🔍 DEBUG: ответ сервиса = {what_is_today_response.text}")

        assert what_is_today_response.status_code == 200
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Новый год", f"Получено: {what_is_today_data.message}"

    @staticmethod
    def stub_get_worldclockap_time():
        """Stub возвращает объект с фиксированной датой"""

        class StubResponse:
            currentDateTime = "2025-05-09T00:00Z"

        return StubResponse()

    def test_what_is_today_by_stub(self, monkeypatch):
        """Тест с использованием Stub"""

        # ПАТЧИМ ДО ВЫЗОВА!
        monkeypatch.setattr(
            "tests.api.test_mock_services.get_worldclockap_time",
            self.stub_get_worldclockap_time
        )

        # ТЕПЕРЬ вызываем — должен вернуться стаб
        world_clock_response = get_worldclockap_time()

        print(f"\n🔍 DEBUG: world_clock_response.currentDateTime = {world_clock_response.currentDateTime}")

        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": world_clock_response.currentDateTime}
        )

        print(f"🔍 DEBUG: ответ сервиса = {what_is_today_response.text}")

        assert what_is_today_response.status_code == 200
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "День Победы", f"Получено: {what_is_today_data.message}"

    def test_what_is_today_by_wiremock(self):
        wiremock_url = "http://localhost:8080/__admin/mappings"  # noqa
        mapping = {
            "request": {
                "method": "GET",
                "url": "/wire/mock/api/json/utc/now"
            },
            "response": {
                "status": 200,
                "body": '''{
                    "$id": "1",
                    "currentDateTime": "2025-03-08T00:00Z",
                    "utcOffset": "00:00",
                    "isDayLightSavingsTime": false,
                    "dayOfTheWeek": "Saturday",
                    "timeZoneName": "UTC",
                    "currentFileTime": 1324567890123,
                    "ordinalDate": "2025-67",
                    "serviceResponse": null
                }'''
            }
        }
        response = requests.post(wiremock_url, json=mapping)
        assert response.status_code == 201

        world_clock_response = requests.get("http://localhost:8080/wire/mock/api/json/utc/now")  # noqa
        assert world_clock_response.status_code == 200

        current_date_time = WorldClockResponse(**world_clock_response.json()).currentDateTime

        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": current_date_time}
        )

        assert what_is_today_response.status_code == 200
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Международный женский день"

    def test_fake_worldclockap(self):
        world_clock_response = get_fake_worldclockap_time()
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время (fake): {current_date_time=}")
        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ")

    def test_fake_what_is_today(self):
        world_clock_response = get_fake_worldclockap_time()
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json={"currentDateTime": world_clock_response.currentDateTime}
        )
        assert what_is_today_response.status_code == 200
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Сегодня нет праздников в России."