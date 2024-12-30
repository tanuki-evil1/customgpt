from flask import current_app, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from app import mail
from app.users.models import User


def get_email_confirmation_token(email):
    """Генерация токена для подтверждения email."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="email-confirm-salt")


def get_reset_password_token(email):
    """Генерация токена для восстановления пароля."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(email, salt="password-reset-salt")


def send_confirmation_email(user):
    token = get_email_confirmation_token(email=user.email)
    link = url_for("auth.confirm_email", token=token, _external=True)
    msg = Message(
        "Подтверждение учетной записи", sender=current_app.config["MAIL_DEFAULT_SENDER"], recipients=[user.email]
    )
    msg.body = f"Для подтверждения учетной записи перейдите по следующей ссылке: {link}"
    mail.send(msg)


def send_reset_password_email(user):
    token = get_reset_password_token(email=user.email)
    link = url_for("auth.change_password", token=token, _external=True)
    msg = Message("Сброс пароля", sender=current_app.config["MAIL_DEFAULT_SENDER"], recipients=[user.email])
    msg.body = f"Для сброса пароля перейдите по следующей ссылке: {link}"
    mail.send(msg)


# Генерация токена для подтверждения email
def verify_email_confirmation_token(token):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt="email-confirm-salt", max_age=3600)
    except BaseException as e:
        raise e
    return User.query.filter_by(email=email).first()


# Генерация токена для восстановления пароля
def verify_reset_password_token(token):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt="password-reset-salt", max_age=600)
    except BaseException as e:
        raise e
    return User.query.filter_by(email=email).first()
