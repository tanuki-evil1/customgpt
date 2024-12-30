from app import db
from app.projects.models import Bot, QuestionAnswer


class ProjectDAO:
    @classmethod
    def get_user_questions(cls, user_id: int):
        """Функция для получения списка вопросов, принадлежащих конкретному пользователю.
        :param user_id: ID пользователя
        :return: Список вопросов пользователя
        """
        try:
            # Выполняем запрос через SQLAlchemy ORM
            questions = (
                db.session.query(QuestionAnswer.question, QuestionAnswer.answer)
                .filter(QuestionAnswer.user_id == user_id)
                .all()
            )
            questions = [(q.question.strip(), q.answer.strip()) for q in questions]

            # Добавляем отладочный вывод
            print(f"Полученные вопросы для пользователя {user_id}: {questions}")

            # Возвращаем список ботов
            return questions if questions else []
        except Exception as e:
            # Обрабатываем возможные ошибки и выводим сообщение об ошибке
            print(f"Ошибка при получении вопросов для пользователя {user_id}: {e!s}")
            return []

    @classmethod
    def get_user_bots(cls, user_id: int):
        """Функция для получения списка ботов, принадлежащих конкретному пользователю.
        :param user_id: ID пользователя
        :return: Список ботов пользователя
        """
        try:
            # Выполняем запрос через SQLAlchemy ORM
            bots = db.session.query(Bot.id, Bot.name).filter(Bot.user_id == user_id).all()

            # Добавляем отладочный вывод
            print(f"Полученные боты для пользователя {user_id}: {bots}")

            # Возвращаем список ботов
            return bots if bots else []
        except Exception as e:
            # Обрабатываем возможные ошибки и выводим сообщение об ошибке
            print(f"Ошибка при получении ботов для пользователя {user_id}: {e!s}")
            return []
