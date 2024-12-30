from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class ChatModelName(str, Enum):
    """Имена моделей"""

    yandex_gpt: str = "Yandex GPT"


class ChatModelDAO(ABC):
    """Базовый класс для ИИ моделей"""

    model_name: ChatModelName

    @classmethod
    @abstractmethod
    def get_model_response(cls, user_input, thread_id, bot_instructions, context, temperature, max_tokens) -> None:
        pass


def choose_model(model_name: ChatModelName) -> Any | None:
    """Выбор модели по имени"""
    from app.ai_models.yandex_gpt.dao import YandexDAO  # noqa Вынести в фабрику отдельно fabric.py

    for model in ChatModelDAO.__subclasses__():
        if model.model_name == model_name:
            return model
