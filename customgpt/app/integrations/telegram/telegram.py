import threading
from time import sleep

import telebot

from app import db  # Импортируем SQLAlchemy сессию
from app.integrations.telegram.models import TelegramIntegration

# Словарь для хранения активных потоков ботов
active_bots = {}


def run_bot(integration_key):
    """Функция для запуска бота с переданным ключом."""
    bot = telebot.TeleBot(integration_key)

    # Удаляем вебхук перед запуском polling
    bot.remove_webhook()

    @bot.message_handler(commands=["start"])
    def send_welcome(message):
        bot.send_message(message.chat.id, "Я работаю")

    @bot.message_handler(commands=["ask_gpt"])
    def ask_gpt(message):
        # prompt = message.text.replace("/ask_gpt ", "")  # Получаем запрос пользователя
        # response = send_prompt_to_model(prompt)  # Передаем запрос в модель
        bot.send_message(message.chat.id, "Привет")  # Отправляем результат пользователю

    print("Бот запущен и ожидает сообщений.")
    bot.polling(none_stop=True, interval=0, timeout=20, skip_pending=True)


def get_telegram_bot_key(bot_id):
    integration = db.session.query(TelegramIntegration).filter_by(bot_id=bot_id).first()
    return integration.token


def create_and_run_bot(bot_id):
    integration_key = get_telegram_bot_key(bot_id)

    if integration_key:
        # Проверяем, работает ли бот уже в другом потоке
        if bot_id in active_bots and active_bots[bot_id].is_alive():
            print(f"Бот с ID {bot_id} уже запущен.")
        else:
            # Запускаем бота в отдельном потоке
            bot_thread = threading.Thread(target=run_bot, args=(integration_key,))
            bot_thread.daemon = True  # Поток завершится при завершении основного процесса
            bot_thread.start()

            # Сохраняем активный поток в словарь
            active_bots[bot_id] = bot_thread
            print(f"Бот с ID {bot_id} запущен в отдельном потоке.")
    else:
        print("Ошибка: не удалось получить ключ бота.")


def check_and_run_bots_on_start():
    """Функция для проверки наличия ключей и запуска ботов при старте приложения."""
    # Здесь можно выполнить запрос в базу данных, чтобы получить все боты с уже сохранёнными ключами
    bots = db.session.query(TelegramIntegration).all()
    for bot in bots:
        if bot.token:
            create_and_run_bot(bot.bot_id)
            sleep(1)  # Пауза, чтобы избежать перегрузки системы
