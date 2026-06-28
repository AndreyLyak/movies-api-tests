# models/error_model.py
from pydantic import BaseModel
from typing import Optional, Union, List


class ErrorResponse(BaseModel):
    """Модель для ответа с ошибкой"""
    detail: Optional[Union[str, List[str]]] = None
    message: Optional[Union[str, List[str]]] = None
    error: Optional[str] = None
    statusCode: Optional[int] = None