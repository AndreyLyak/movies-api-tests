import json
import logging

logger = logging.getLogger(__name__)


class CustomRequester:

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def send_request(self, method, endpoint, data=None, params=None, expected_status=200):
        url = f"{self.base_url}{endpoint}"

        logger.info(f"➡️  {method} {url}")
        if data:
            logger.debug(f" Данные: {json.dumps(data, ensure_ascii=False)[:200]}")

        response = self.session.request(method, url, json=data, params=params)

        logger.info(f"⬅️  Статус: {response.status_code}")

        if response.status_code != expected_status:
            logger.error(f" Ожидался статус {expected_status}, получили {response.status_code}")
            logger.error(f"Ответ: {response.text[:500]}")
            raise AssertionError(
                f"Ожидался статус {expected_status}, получили {response.status_code}\n"
                f"Ответ: {response.text[:500]}"
            )

        return response