// Функция для переключения видимости пароля
function togglePasswordVisibility(inputId, iconId) {
    const passwordField = document.getElementById(inputId);
    const icon = document.getElementById(iconId).querySelector('i');

    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        passwordField.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}

// Применение функции для полей пароля и повторного пароля после загрузки DOM
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('toggle-password').addEventListener('click', function () {
        togglePasswordVisibility('password', 'toggle-password');
    });

    document.getElementById('toggle-confirm-password').addEventListener('click', function () {
        togglePasswordVisibility('confirm-password', 'toggle-confirm-password');
    });
});
