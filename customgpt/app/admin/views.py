from flask import redirect, url_for
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView


# Представление для работы с компаниями
class CompanyView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True


# Кастомное представление для вопросов-ответов, фильтруется по компании через связь со стадией
# class QuestionAnswerView(ModelView):
#     form_columns = ['question', 'answer', 'stage']
#
#     def get_query(self):
#         # Фильтрация по компании через стадию
#         return super(QuestionAnswerView, self).get_query().join(Stage).filter(Stage.company_id == self.company_id)
#
#     def __init__(self, session, company_id, **kwargs):
#         super(QuestionAnswerView, self).__init__(QuestionAnswer, session, **kwargs)
#         self.company_id = company_id
#         # Генерируем уникальное имя для каждого представления
#         self.endpoint = f'qa_{company_id}'


# Кастомная страница для управления стадиями и вопросами внутри компании
class CompanyManagementView(BaseView):
    @expose("/")
    def index(self):
        # Главная страница управления компаниями
        return self.render("admin/company_management.html")

    @expose("/<int:company_id>/")
    def manage_company(self, company_id):
        # Переход на страницу управления стадиями и вопросами конкретной компании
        return redirect(url_for(f"stage_{company_id}.index_view"))
