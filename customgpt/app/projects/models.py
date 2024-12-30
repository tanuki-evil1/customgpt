from datetime import datetime

from sqlalchemy import Column, String

from app import db
from app.integrations.models import bots_integrations


# Модель бота
class Bot(db.Model):
    __tablename__ = "bots"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default="остановлен")  # Статус бота: работает, остановлен, ошибка
    instructions = db.Column(db.String, nullable=True)
    temperature = db.Column(db.Float, default=0.5)

    config_name = db.Column(db.String)

    file_names = db.Column(db.String)  # Имена файлов

    chat_model_id = db.Column(db.Integer, db.ForeignKey("chat_models.id"))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Bot {self.name}, Status: {self.status}>"

    # Связь с пользователем (владелец бота)
    user = db.relationship("User", back_populates="bots")
    integrations = db.relationship("Integration", secondary=bots_integrations, back_populates="bots")
    chat_model = db.relationship("ChatModel", back_populates="bots")


# Модель для таблицы вопросов и ответов
class QuestionAnswer(db.Model):
    __tablename__ = "questions_answers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<QuestionAnswer(id={self.id}, question={self.question}, answer={self.answer})>"

    user = db.relationship("User", back_populates="questions_answers")
