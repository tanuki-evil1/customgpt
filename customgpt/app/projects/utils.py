import pdfplumber
from flask_wtf import FlaskForm
from wtforms import HiddenField

from app import db
from app.projects.models import Bot


# Определяем форму для CSRF защиты
class DummyForm(FlaskForm):
    csrf_token = HiddenField()


def get_uploaded_files(bot_id):
    """Функция для получения списка загруженных файлов для конкретного бота по bot_id."""
    # Выполняем запрос через SQLAlchemy для получения списка файлов
    files = (
        db.session.query(Bot.file_names)
        .filter(
            Bot.id == bot_id,
            Bot.file_names.isnot(None),
        )
        .all()
    )

    # Преобразуем результат в список (если есть хотя бы один файл)
    file_list = [file[0] for file in files] if files else []
    print(file_list)  # Выводим список файлов для отладки
    return file_list


def allowed_file(filename):
    # Задайте допустимое расширение файла
    allowed_extension = "pdf"

    # Проверка, что '.' присутствует в имени файла и последний фрагмент после точки
    # (расширение файла) совпадает с допустимым расширением
    return "." in filename and filename.rsplit(".", 1)[1].lower() == allowed_extension


# Функция для извлечения FAQ из PDF документа и вставки в бд
def extract_faq_from_pdf(pdf_file_stream, user_id):
    """Извлекает вопросы и ответы из PDF-файла (переданного как поток) и вставляет их в таблицу QuestionAnswer
    для указанного user_id.
    """
    # Открываем PDF-документ из потока (файловый объект)
    with pdfplumber.open(pdf_file_stream) as pdf:
        question = None
        answer_lines = []
        qa_pairs = []

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")

                for line in lines:
                    if line.startswith("#"):  # Определяем вопрос
                        if question and answer_lines:
                            answer = " ".join(answer_lines).strip()
                            qa_pairs.append((question, answer))

                        # Новый вопрос
                        question = line.replace("#", "").strip()
                        answer_lines = []
                    else:
                        # Добавляем строки в ответ
                        answer_lines.append(line.strip())

        # Добавляем последний вопрос и ответ, если они есть
        if question and answer_lines:
            answer = " ".join(answer_lines).strip()
            qa_pairs.append((question, answer))

    return qa_pairs
