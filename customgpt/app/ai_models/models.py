from app import db


# Модель интеграции ai
class ChatModel(db.Model):
    __tablename__ = "chat_models"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    bots = db.relationship("Bot", back_populates="chat_model")
