from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from . import config
from .database import Base

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()


def create_app():
    # Инициализация приложения Flask
    app = Flask(__name__)
    # Настройки приложения
    app.config.from_object(config.Config)

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Настройка страницы для неавторизованных пользователей
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Пожалуйста, войдите в систему."

    # Регистрация Blueprints
    from app.auth.routes import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from app.projects.routes import blueprint as project_blueprint

    app.register_blueprint(project_blueprint, url_prefix="/projects")

    from app.integrations.routes import integration as integration_blueprint

    app.register_blueprint(integration_blueprint, url_prefix="/integrations")

    from app.analytics.routes import analytic as analytics_blueprint

    app.register_blueprint(analytics_blueprint)

    # Инициализируем Flask-Admin и указываем URL для админки
    admin = Admin(app, name="Admin Panel", url="/myadmin", template_mode="bootstrap4")

    from app.projects.models import Bot, QuestionAnswer

    admin.add_view(ModelView(QuestionAnswer, db.session, name="Вопросы и ответы"))
    admin.add_view(ModelView(Bot, db.session, name="Боты"))

    from app.integrations.models import Integration

    admin.add_view(ModelView(Integration, db.session, name="Интеграция бота"))

    from app.users.models import User

    admin.add_view(ModelView(User, db.session, name="Пользователь"))

    from app.ai_models.models import ChatModel

    admin.add_view(ModelView(ChatModel, db.session, name="Интеграция ai"))

    from app.integrations.telegram.models import TelegramIntegration

    admin.add_view(ModelView(TelegramIntegration, db.session, name="Интеграция телеграм"))

    return app
