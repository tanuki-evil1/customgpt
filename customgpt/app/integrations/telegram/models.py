from app import db


class TelegramIntegration(db.Model):
    __tablename__ = "telegram_integrations"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    bot_id = db.Column(db.Integer, db.ForeignKey("bots.id"), nullable=False)
