# db_requester/db_creds.py
import os
from dotenv import load_dotenv

load_dotenv()


class MoviesDbCreds:
    """Класс для работы с кредами через класс (новый подход)"""
    HOST = os.getenv('DB_MOVIES_HOST')
    PORT = os.getenv('DB_MOVIES_PORT')
    DATABASE_NAME = os.getenv('DB_MOVIES_NAME')
    USERNAME = os.getenv('DB_MOVIES_USERNAME')
    PASSWORD = os.getenv('DB_MOVIES_PASSWORD')


def get_db_credentials():
    """Функция для работы с кредами (старый подход, для обратной совместимости)"""
    return {
        "dbname": os.getenv("DB_MOVIES_NAME"),
        "user": os.getenv("DB_MOVIES_USERNAME"),
        "password": os.getenv("DB_MOVIES_PASSWORD"),
        "host": os.getenv("DB_MOVIES_HOST"),
        "port": os.getenv("DB_MOVIES_PORT")
    }