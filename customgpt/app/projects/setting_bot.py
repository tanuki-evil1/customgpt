import multiprocessing
import time

from flask import current_app

from app import db
from app.projects.models import Bot


# Функция для запуска бота с обновлением статуса
def start_bot(bot_id, api_key):
    with current_app.app_context():  # Используем current_app вместо app
        update_bot_status(bot_id, "работает")  # Обновляем статус на "работает"
    while True:
        try:
            print(f"Бот {bot_id} запущен с ключом {api_key}")
            time.sleep(10)
        except Exception as e:
            with current_app.app_context():  # Используем current_app для обработки ошибок
                print(f"Ошибка в работе бота {bot_id}: {e!s}")
                update_bot_status(bot_id, "ошибка")  # Обновляем статус на "ошибка"
            break


# Функция для остановки бота с обновлением статуса
def stop_bot(process, bot_id):
    if process.is_alive():
        process.terminate()
        with current_app.app_context():
            update_bot_status(bot_id, "остановлен")  # Обновляем статус на "остановлен"
        print(f"Бот {bot_id} остановлен")
    else:
        print("Процесс уже завершен")


# Функция для перезапуска бота с обновлением статуса
def restart_bot(bot_id, api_key, process):
    stop_bot(process, bot_id)
    new_process = multiprocessing.Process(target=start_bot, args=(bot_id, api_key))
    new_process.start()
    update_bot_status(bot_id, "работает")  # Обновляем статус на "работает"
    return new_process


# Функция для обновления статуса в базе данных
def update_bot_status(bot_id, status):
    try:
        # Используем контекст приложения
        with current_app.app_context():
            # Получаем бота по ID
            bot = db.session.query(Bot).filter_by(id=bot_id).first()
            if bot:
                bot.status = status
                db.session.commit()
                print(f"Статус бота {bot_id} обновлен на '{status}'")
            else:
                print(f"Бот с id {bot_id} не найден.")
    except Exception as e:
        db.session.rollback()  # Откатываем изменения в случае ошибки
        print(f"Ошибка обновления статуса бота {bot_id}: {e}")
