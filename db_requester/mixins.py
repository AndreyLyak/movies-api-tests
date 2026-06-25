# db_requester/mixins.py
from typing import Dict, Any


class ToDictMixin:
    """
    Миксин, добавляющий метод to_dict для преобразования SQLAlchemy-модели в словарь.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект модели в словарь.
        """
        result = {}
        for column in self.__table__.columns:  # type: ignore[attr-defined]
            value = getattr(self, column.name)
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            result[column.name] = value
        return result