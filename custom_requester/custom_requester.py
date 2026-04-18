import json


class CustomRequester:

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def send_request(self, method, endpoint, data=None, expected_status=200):

        url = f"{self.base_url}{endpoint}"

        response = self.session.request(method, url, json=data)

        print(f"  {method} {url}")
        print(f" Данные: {json.dumps(data, ensure_ascii=False)[:200] if data else 'нет'}")
        print(f"  Статус: {response.status_code}")

        # Проверяем статус
        if response.status_code != expected_status:
            raise AssertionError(
                f" Ожидался статус {expected_status}, "
                f"получили {response.status_code}\n"
                f"Ответ: {response.text[:500]}"
            )

        return response