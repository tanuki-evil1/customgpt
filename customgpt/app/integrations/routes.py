from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app.integrations.forms import TelegramForm
from app.integrations.telegram.dao import TelegramDAO
from app.integrations.telegram.telegram import create_and_run_bot

integration = Blueprint("integrations", __name__)


@integration.route("/integration")
@login_required
def integration_page():
    bot_id = request.args.get("bot_id")

    return render_template(
        "integrations/integration.html", bot_id=bot_id, username=current_user.username, email=current_user.email
    )


@integration.route("/telegram_integration/<int:bot_id>", methods=["GET", "POST"])
@login_required
def telegram_integration(bot_id):
    form = TelegramForm()
    if form.validate_on_submit():
        TelegramDAO.add_integration(bot_id, token=form.token.data)
        create_and_run_bot(bot_id)
        return redirect(url_for("projects.setting_bot", bot_id=bot_id))

    return render_template(
        "integrations/telegram_integration.html",
        bot_id=bot_id,
        username=current_user.username,
        email=current_user.email,
        form=form,
    )
