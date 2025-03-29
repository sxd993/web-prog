document.addEventListener('DOMContentLoaded', function () {
    const emailInput = document.getElementById('email');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const password2Input = document.getElementById('password2');
    const submitBtn = document.getElementById('submitBtn');
    const form = document.getElementById('registrationForm');

    // Флаги валидности полей
    let isEmailValid = false;
    let isUsernameValid = false;
    let isPasswordValid = false;
    let isPassword2Valid = false;

    // Проверка email на лету с AJAX
    emailInput.addEventListener('input', function () {
        const email = emailInput.value.trim();
        const emailError = document.getElementById('emailError');

        // Сброс состояния
        emailError.textContent = '';
        emailInput.classList.remove('is-invalid', 'is-valid');
        isEmailValid = false;
        updateSubmitButton();

        if (!email) return;

        // 1. Проверка формата email
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            emailError.textContent = 'Введите корректный email';
            emailInput.classList.add('is-invalid');
            return;
        }

        // 2. AJAX-проверка уникальности
        fetch('/api/check-email/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ email: email })
        })
            .then(response => {
                if (!response.ok) throw new Error('Ошибка сервера');
                return response.json();
            })
            .then(data => {
                if (data.is_unique) {
                    emailInput.classList.add('is-valid');
                    isEmailValid = true;
                } else {
                    emailError.textContent = 'Этот email уже занят';
                    emailInput.classList.add('is-invalid');
                }
            })
            .catch(error => {
                console.error('Ошибка проверки email:', error);
                emailError.textContent = 'Ошибка сервера при проверке';
                emailInput.classList.add('is-invalid');
            })
            .finally(() => {
                updateSubmitButton();
            });
    });

    // Проверка имени пользователя на лету
    usernameInput.addEventListener('input', function () {
        const username = usernameInput.value.trim();
        const usernameError = document.getElementById('usernameError');

        if (!username) {
            usernameError.textContent = '';
            usernameInput.classList.remove('is-invalid', 'is-valid');
            isUsernameValid = false;
            updateSubmitButton();
            return;
        }

        if (username.length < 3) {
            usernameError.textContent = 'Имя пользователя должно содержать минимум 3 символа';
            usernameInput.classList.add('is-invalid');
            usernameInput.classList.remove('is-valid');
            isUsernameValid = false;
        } else {
            usernameError.textContent = '';
            usernameInput.classList.remove('is-invalid');
            usernameInput.classList.add('is-valid');
            isUsernameValid = true;
        }

        updateSubmitButton();
    });

    // Проверка пароля на лету
    passwordInput.addEventListener('input', function () {
        const password = passwordInput.value;
        const passwordError = document.getElementById('passwordError');

        if (!password) {
            passwordError.textContent = '';
            passwordInput.classList.remove('is-invalid', 'is-valid');
            isPasswordValid = false;
            updateSubmitButton();
            return;
        }

        if (password.length < 6) {
            passwordError.textContent = 'Пароль должен содержать минимум 6 символов';
            passwordInput.classList.add('is-invalid');
            passwordInput.classList.remove('is-valid');
            isPasswordValid = false;
        } else {
            passwordError.textContent = '';
            passwordInput.classList.remove('is-invalid');
            passwordInput.classList.add('is-valid');
            isPasswordValid = true;
        }

        // Проверка совпадения паролей, если второй пароль уже введён
        if (password2Input.value) {
            validatePasswordMatch();
        }

        updateSubmitButton();
    });

    // Проверка подтверждения пароля на лету
    password2Input.addEventListener('input', validatePasswordMatch);

    function validatePasswordMatch() {
        const password = passwordInput.value;
        const password2 = password2Input.value;
        const password2Error = document.getElementById('password2Error');

        if (!password2) {
            password2Error.textContent = '';
            password2Input.classList.remove('is-invalid', 'is-valid');
            isPassword2Valid = false;
            updateSubmitButton();
            return;
        }

        if (password !== password2) {
            password2Error.textContent = 'Пароли не совпадают';
            password2Input.classList.add('is-invalid');
            password2Input.classList.remove('is-valid');
            isPassword2Valid = false;
        } else {
            password2Error.textContent = '';
            password2Input.classList.remove('is-invalid');
            password2Input.classList.add('is-valid');
            isPassword2Valid = true;
        }

        updateSubmitButton();
    }


    // Обновление состояния кнопки отправки
    function updateSubmitButton() {
        submitBtn.disabled = !(isEmailValid && isUsernameValid && isPasswordValid && isPassword2Valid);
    }

    // Вспомогательная функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Обработка отправки формы
    form.addEventListener('submit', function (e) {
        if (!isEmailValid || !isUsernameValid || !isPasswordValid || !isPassword2Valid) {
            e.preventDefault();
            alert('Пожалуйста, исправьте ошибки в форме перед отправкой.');
        }
    });
});