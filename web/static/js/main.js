// Основной JavaScript файл

// Автоматическое скрытие алертов через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Подтверждение перед отправкой формы
document.querySelectorAll('.confirm-form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
        if (!confirm('Вы уверены?')) {
            e.preventDefault();
        }
    });
});

// Валидация форм на клиенте
document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Проверка email
        const emailInputs = form.querySelectorAll('input[type="email"]');
        emailInputs.forEach(function(input) {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(input.value)) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        // Проверка пароля (минимум 6 символов)
        const passwordInputs = form.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(function(input) {
            if (input.value.length < 6) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
        }
    });
});

// Динамическое обновление баланса
async function updateBalance() {
    try {
        const response = await fetch('/api/v1/balance/');
        if (response.ok) {
            const data = await response.json();
            const balanceElements = document.querySelectorAll('.balance-display');
            balanceElements.forEach(el => {
                el.textContent = data.balance;
            });
        }
    } catch (error) {
        console.error('Ошибка обновления баланса:', error);
    }
}

// Обновляем баланс каждые 30 секунд
if (document.querySelector('.balance-display')) {
    setInterval(updateBalance, 30000);
}

// Анимация для карточек при загрузке
document.querySelectorAll('.card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    setTimeout(() => {
        card.style.transition = 'all 0.5s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    }, index * 100);
});
