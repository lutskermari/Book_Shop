import requests
import logging

logger = logging.getLogger(__name__)

ANALYTICS_SERVICE_URL = "http://analytics-web:8001/api/analytics/track-sale/"


def send_sale_to_analytics(book_id, book_title, quantity, total_price):
    payload = {
        "book_id": book_id,
        "book_title": book_title,
        "quantity": quantity,
        "total_price": str(total_price),
    }

    try:
        response = requests.post(ANALYTICS_SERVICE_URL, json=payload, timeout=3)
        if response.status_code == 201:
            logger.info(f"Успішно відправлено аналітику для книги {book_title}")
        else:
            logger.warning(
                f"Аналітика повернула помилку: {response.status_code} {response.text}"
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"Не вдалося з'єднатися із сервісом аналітики: {e}")
