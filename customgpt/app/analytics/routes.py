from flask import Blueprint, render_template
from flask_login import login_required

# Создаём blueprint для аналитики
analytic = Blueprint("analytic", __name__)


@analytic.route("/analytic")
@login_required
def analytic_page():
    return render_template("analytics/analytic.html")
