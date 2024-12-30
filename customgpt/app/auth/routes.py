from datetime import timedelta

from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.users.models import User

from .forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm
from .mail import (
    send_confirmation_email,
    send_reset_password_email,
    verify_email_confirmation_token,
    verify_reset_password_token,
)

auth = Blueprint("auth", __name__)


@auth.route("/")
@login_required
def index():
    """Главная страница приложения."""
    username = current_user.username
    email = current_user.email
    return render_template("auth/index.html", username=username, email=email)


@auth.route("/registration", methods=["GET", "POST"])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))  # Если пользователь уже авторизован

    form = RegistrationForm()
    if form.validate_on_submit():  # POST
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        send_confirmation_email(user)  # Отправка подтверждающего письма

        flash("Пожалуйста, подтвердите вашу почту для завершения регистрации.")
        return redirect(url_for("auth.letter_registration", user_email=form.email.data))

    return render_template("auth/registration.html", form=form)


@auth.route("/letter_registration")
def letter_registration():
    user_email = request.args.get("user_email")
    return render_template("auth/letter_registration.html", user_email=user_email)


@auth.route("/confirm/<token>")
def confirm_email(token):
    user = verify_email_confirmation_token(token)
    if user:
        user.confirmed = True
        db.session.commit()
        flash("Ваш аккаунт подтвержден.")
    else:
        flash("Неверный или просроченный токен.")

    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=form.remember_me.data, duration=timedelta(days=7))
            flash("Вы успешно вошли в систему.")
            return redirect(url_for("auth.index"))
        flash("Неверные данные для входа.")

    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы успешно вышли из системы.")
    return redirect(url_for("auth.login"))


@auth.route("/recovery_password", methods=["GET", "POST"])
def recovery_password():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_password_email(user)
            flash("Инструкции по восстановлению пароля отправлены на вашу почту.")
            return redirect(url_for("auth.confirm_reset_password_email"))
        flash("Пользователь с таким email не найден.")

    return render_template("auth/recovery_password.html", form=form)


@auth.route("/reset_password/email")
def confirm_reset_password_email():
    return render_template("auth/recovery_password_email.html")


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def change_password(token):
    user = verify_reset_password_token(token)
    print(user)
    if not user:
        flash("Неверный или просроченный токен.")
        return redirect(url_for("auth.login"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Ваш пароль был обновлен! Вы можете войти с новым паролем.")
        return redirect(url_for("auth.login"))

    return render_template("auth/changing_the_password.html", form=form, token=token)
