import os

from app import create_app
from app.integrations.telegram.telegram import check_and_run_bots_on_start

app = create_app()

if __name__ == "__main__":
    if os.getenv("WERKZEUG_RUN_MAIN") == "true":
        with app.app_context():
            print("Контекст приложения Flask активен")
            check_and_run_bots_on_start()

    print("Запуск приложения...")
    app.run(debug=True)
