from app.integrations.dao import IntegrationDAO
from app.integrations.telegram.models import TelegramIntegration
from app import db


# Работа с базой данных
class TelegramDAO(IntegrationDAO):
    @staticmethod
    def add_integration(bot_id, token: str):
        telegram_integration = TelegramIntegration(token=token, bot_id=bot_id)
        db.session.add(telegram_integration)
        db.session.commit()

    @staticmethod
    def get_token_by_id(bot_id):
        return TelegramIntegration.query.filter_by(bot_id=bot_id).first().token

    @staticmethod
    def get_all_bots():
        return TelegramIntegration.query.all()
