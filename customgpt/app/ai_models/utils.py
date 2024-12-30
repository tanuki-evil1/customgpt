from typing import List, Tuple


def build_context(qa_pairs: List[Tuple[str, str]]) -> str:
    """Формируем контекст - Вопрос/Ответ для ИИ моделей"""
    context = ""
    for question, answer in qa_pairs:
        context += f"Вопрос: {question}\nОтвет: {answer}\n---\n"
    return context
