document.addEventListener('DOMContentLoaded', function() {
    // Ползунок температуры
    const rangeInput = document.getElementById('temperatureRange');
    const valueDisplay = document.getElementById('value'); // Получаем элемент для отображения значения

    rangeInput.addEventListener('input', function() {
        // Получаем текущее значение ползунка
        const value = this.value;

        // Обновляем текстовое значение в элементе <span>
        valueDisplay.textContent = value;

        // Высчитываем процент заполнения
        const percentage = (value - this.min) / (this.max - this.min) * 100;

        // Обновляем стиль фона ползунка с помощью градиента
        this.style.background = `linear-gradient(to right, #615EF0 0%, #615EF0 ${percentage}%, #E1E3E6 ${percentage}%, #E1E3E6 100%)`;
    });

    // Устанавливаем начальный фон для ползунка и значение
    rangeInput.dispatchEvent(new Event('input'));

    // Функция отправки сообщений
    function sendMessage() {
        const userInput = document.getElementById('user-input').value;
        if (userInput) {
            fetch('{{ url_for("main.setting_bot", bot_id=bot_id) }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': '{{ form.csrf_token._value() }}'
                },
                body: new URLSearchParams({
                    'message': userInput
                })
            })
            .then(response => response.json())
            .then(data => {
                const chatMessages = document.getElementById('chat-messages');
                const userMessage = document.createElement('div');
                userMessage.className = 'alert alert-secondary';
                userMessage.role = 'alert';
                userMessage.innerText = userInput;
                chatMessages.appendChild(userMessage);

                const botMessage = document.createElement('div');
                botMessage.className = 'alert alert-light';
                botMessage.role = 'alert';
                botMessage.innerHTML = `<img src="{{ url_for('static', filename='images/avatar2.png') }}" alt="Аватар бота"> <p>${data.response}</p>`;
                chatMessages.appendChild(botMessage);

                document.getElementById('user-input').value = '';
            })
            .catch(error => console.error('Error:', error));
        }
    }

    // Обработчик для отправки сообщений по клику
    document.querySelector('input[type="image"]').addEventListener('click', sendMessage);

    // Функция обновления чата
    function refreshChat() {
        location.reload(); // Перезагружает всю страницу
    }

    // Обработчик клика для кнопки "Обновить"
    document.querySelector('.btn-primary').addEventListener('click', refreshChat);

    // Обработчик меню
    document.getElementById('menu-toggle').addEventListener('click', function () {
        document.getElementById('wrapper').classList.toggle('toggled');
    });

    // JavaScript для обработки отправки формы создания бота
    const createBotForm = document.getElementById('createBotForm');
    if (createBotForm) {
        createBotForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Предотвращаем перезагрузку страницы
            var botName = document.getElementById('botName').value;

            // AJAX запрос на сервер
            fetch('/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ bot_name: botName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Перенаправление на страницу настроек бота
                    window.location.href = data.redirect_url;
                } else {
                    alert('Ошибка при создании бота: ' + data.message);
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    }
});
