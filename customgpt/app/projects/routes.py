from datetime import datetime

import pytz
from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.ai_models.dao import choose_model
from app.ai_models.models import ChatModel
from app.projects.dao import ProjectDAO
from app.projects.models import Bot, QuestionAnswer
from app.users.models import User

from .utils import DummyForm, allowed_file, extract_faq_from_pdf, get_uploaded_files

blueprint = Blueprint("projects", __name__)


@blueprint.route("/all_projects")
@login_required
def all_projects():
    """Страница со списком всех проектов пользователя."""
    # Получаем информацию о пользователе через SQLAlchemy ORM
    user = current_user
    if not user:
        flash("Ошибка при загрузке данных пользователя.", "danger")
        return redirect(url_for("auth.login"))

    username, email = user.username, user.email  # Извлекаем имя и email

    # Получаем список ботов
    bots = ProjectDAO.get_user_bots(user.id)

    # Передаем username и email в шаблон
    return render_template("projects/all_projects.html", bots=bots, username=username, email=email)


@blueprint.route("/create", methods=["POST"])
@login_required
def create_bot():
    """Маршрут для создания нового бота пользователем."""
    user_id = current_user.id
    data = request.json
    bot_name = data.get("name")

    if not bot_name:
        return jsonify({"success": False, "message": "Название бота не может быть пустым."})

    # Проверяем, существует ли уже бот с таким же именем у этого пользователя через SQLAlchemy
    existing_bot = Bot.query.filter_by(user_id=user_id, name=bot_name).first()

    if existing_bot:
        return jsonify(
            {"success": False, "message": "Бот с таким названием уже существует. Пожалуйста, выберите другое имя."}
        )

    # Создаем нового бота через SQLAlchemy ORM
    new_bot = Bot(user_id=user_id, name=bot_name, created_at=datetime.now(pytz.utc))

    try:
        db.session.add(new_bot)
        db.session.commit()  # Сохраняем изменения в базе данных

        # Получаем id нового бота для перенаправления
        redirect_url = url_for("projects.setting_bot", bot_id=new_bot.id)
        return jsonify(
            {"success": True, "message": "Бот успешно создан!", "bot_id": new_bot.id, "redirect_url": redirect_url}
        )
    except Exception as e:
        db.session.rollback()  # Откат транзакции в случае ошибки
        return jsonify({"success": False, "message": f"Не удалось создать бота. Ошибка: {e!s}"})


# projects
@blueprint.route("/delete_bot/<int:bot_id>", methods=["POST", "GET"])  # Добавляем GET для редиректа
@login_required
def delete_bot(bot_id):
    """Маршрут для удаления бота."""
    # Проверяем, существует ли бот с данным ID через SQLAlchemy
    bot = Bot.query.filter_by(id=bot_id).first()
    if not bot:
        flash("Бот с указанным ID не существует.", "danger")
        return redirect(url_for("projects.all_projects"))

    # Удаляем бота из базы данных
    try:
        db.session.delete(bot)
        db.session.commit()  # Коммитим изменения в базе данных
        flash("Бот успешно удален!", "success")
        print("Вроде ок")
    except Exception as e:
        db.session.rollback()  # Откат транзакции при ошибке
        flash(f"Ошибка при удалении бота: {e!s}", "danger")

    return redirect(url_for("projects.all_projects"))


@blueprint.route("/chatbot/<int:bot_id>", methods=["POST"])
@login_required
def chatbot(bot_id):
    user_input = request.form.get("message")
    user_id = current_user.id
    print(f"Received user input: {user_input}")  # Логируем ввод пользователя

    if user_input:
        # Загрузка текущих настроек бота из базы данных через SQLAlchemy
        bot = Bot.query.filter_by(id=bot_id).first()
        if bot:
            bot_instructions = bot.instructions
            temperature = bot.temperature
            chat_model = ChatModel.query.filter_by(id=bot.chat_model_id).first()
        else:
            chat_model = ChatModel.query.filter_by(id=1).first()
            bot_instructions, temperature = "", 0.5  # Значения по умолчанию

        # Запрос к модели через функцию get_model_response
        chat = choose_model(chat_model.name)
        context = ProjectDAO.get_user_questions(user_id)
        thread_id = f"{bot_id}"  # Получать thread_id надо из интеграций
        generated_text = chat.get_model_response(user_input, thread_id, bot_instructions, context, temperature)
        print(f"Generated text: {generated_text}")  # Логируем сгенерированный текст

        return jsonify({"response": generated_text})

    print("No input provided")  # Логируем отсутствие ввода
    return jsonify({"response": "No input provided"}), 400


@blueprint.route("/setting_bot/<int:bot_id>", methods=["GET", "POST"])
@login_required
def setting_bot(bot_id: int):
    """Маршрут для настроек бота."""
    session["bot_id"] = bot_id  # Сохраняем bot_id в сессии
    form = DummyForm()  # CSRF защита

    # Проверка существования бота
    bot = db.session.query(Bot).filter_by(id=bot_id).first()
    if not bot:
        flash("Бот с таким ID не существует.", "danger")
        return redirect(url_for("projects.all_projects"))

    bot_name = bot.name

    # Получение данных о пользователе
    user_id = current_user.id
    if user_id:
        user = db.session.query(User).filter_by(id=user_id).first()
        if user:
            username = user.username
            email = user.email
        else:
            flash("Не удалось загрузить данные пользователя.", "danger")
            return redirect(url_for("auth.login"))
    else:
        flash("Вы не авторизованы. Пожалуйста, войдите в систему.", "warning")
        return redirect(url_for("auth.login"))

    # Получаем список файлов для текущего бота
    file_list = get_uploaded_files(bot_id)

    # Получаем список моделей из таблицы select_model
    models = db.session.query(ChatModel).all()
    model_list = [{"id": model.id, "model_name": model.name} for model in models]

    if request.method == "POST":
        selected_model_id = request.form.get("model_id")
        if selected_model_id:
            selected_model_id = int(selected_model_id)
        else:
            selected_model_id = 1  # Значение по умолчанию

        # Обработка загруженного файла
        file = request.files.get("infoFile")
        all_text = []
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            qa_pairs = extract_faq_from_pdf(file, user_id)

            # Вставляем данные в таблицу QuestionAnswer для данного user_id
            for question, answer in qa_pairs:
                new_qa = QuestionAnswer(
                    user_id=user_id,  # Привязка к конкретному пользователю
                    question=question,
                    answer=answer,
                )
                db.session.add(new_qa)

            db.session.commit()

            flash(f"{qa_pairs} FAQ успешно извлечены из файла.", "success")

        bot_instructions = "\n".join(all_text)
        bot_more_info = request.form.get("botMoreInfo", "")
        temperature = float(request.form.get("temperature", 0.5))
        current_time = datetime.now(pytz.utc)

        # Проверка существования записи в bot_settings
        bot = db.session.query(Bot).filter_by(id=bot_id).first()

        if bot:
            # Обновление существующих настроек
            bot.info = bot_instructions
            bot.instructions = bot_more_info
            bot.temperature = temperature
            bot.file_names = filename
            bot.chat_model_id = selected_model_id
            bot.created_at = current_time
            flash("Настройки успешно обновлены!", "success")
        else:
            # Создание новых настроек
            new_bot = Bot(
                id=bot_id,
                name=bot_name,
                instructions=bot_instructions,
                temperature=temperature,
                created_at=current_time,
                file_name=filename,
                chat_model_id=selected_model_id,
            )
            db.session.add(new_bot)
            flash("Настройки успешно сохранены!", "success")

        # Логика обновления связи между ботом и моделью
        chat_model = db.session.query(ChatModel).filter_by(id=selected_model_id).first()

        if chat_model:
            bot.chat_model_id = selected_model_id
            print(bot.chat_model_id, bot)
            print(f"Запись для бота {bot_name} обновлена на модель ID {selected_model_id}.")
        else:
            new_link = Bot(id=bot_id, chat_model_id=selected_model_id)
            db.session.add(new_link)
            print(f"Запись для бота {bot_name} добавлена с моделью ID {selected_model_id}.")

        db.session.commit()  # Сохраняем изменения в базе данных
        return redirect(url_for("projects.setting_bot", bot_id=bot_id))

    # Если запрос GET, загружаем текущие настройки для отображения в форме
    bot = db.session.query(Bot).filter_by(id=bot_id).first()

    if bot:
        bot_instructions = bot.instructions
        temperature = bot.temperature
        selected_model_id = bot.chat_model
    else:
        bot_instructions, temperature, selected_model_id = "", 0.5, 1

    # Получаем текущую модель
    # current_model = db.session.query(Bot).join(Bot, Bot.id == Bot.model_id).filter(Bot.id == bot_id).first()
    #
    # if current_model:
    #     selected_model_id = current_model.id
    # else:
    #     selected_model_id = 1  # ID модели по умолчанию (Chat GPT 3.5)

    return render_template(
        "projects/setting_bot.html",
        bot_id=bot_id,
        bot_name=bot_name,
        form=form,
        bot_instructions=bot_instructions,
        temperature=temperature,
        selected_model_id=selected_model_id,
        file_list=file_list,
        username=username,
        email=email,
        models=model_list,
    )


@blueprint.route("/delete_file/<int:bot_id>/<file_name>", methods=["POST"])
@login_required
def delete_file(bot_id, file_name):
    """Маршрут для удаления файла."""
    # Обновляем запись в базе данных, устанавливая file_name в NULL для бота с указанным bot_id
    bot_settings = db.session.query(Bot).filter_by(id=bot_id, file_name=file_name).first()

    if bot_settings:
        bot_settings.file_names = None  # Устанавливаем значение NULL для file_name
        db.session.commit()  # Сохраняем изменения в базе данных
        flash("Файл успешно удалён!", "success")
    else:
        flash("Файл не найден или уже был удалён.", "danger")

    return redirect(url_for("setting_bot.setting_bot", bot_id=bot_id))
