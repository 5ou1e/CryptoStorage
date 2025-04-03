<script>
    // Логика обновления кошелька
    function updateWalletStats() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Получение CSRF токена
        const updateWalletStatsUrl = "/api/v1/wallets/refresh_stats"; // Новый эндпоинт для создания задачи

        const data = { address: walletAddress };  // Ваш адрес кошелька

        fetch(updateWalletStatsUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data) // Отправка данных в теле запроса
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                showNotification('Обновление поставлено в очередь!', 'success');
                console.log(data.result.task_id);  // Получение task_id из ответа
                checkStatsUpdateTaskStatus(data.result.task_id);  // Проверка статуса задачи
            } else {
                showNotification('Ошибка! Попробуйте снова.', 'error');
            }
        })
        .catch(error => {
            alert('Ошибка: ' + error);
        });
    }

    // Функция для формирования URL для проверки статуса задачи
    function getUpdateTaskStatusUrl(taskId) {
        return `/api/v1/wallets/refresh_stats/${taskId}/status`;  // Новый эндпоинт для получения статуса задачи
    }

    // Функция для опроса статуса задачи
    function checkStatsUpdateTaskStatus(taskId) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Получение CSRF токена
        const interval = setInterval(function() {
            const updateWalletStatsTaskStatusUrl = getUpdateTaskStatusUrl(taskId);  // Получаем URL для статуса

            fetch(updateWalletStatsTaskStatusUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                // Если статус задачи успешен, останавливаем интервал и перезагружаем страницу
                if (data.result.status === 'success') {
                    clearInterval(interval);
                    showNotification('Статистика обновлена!', 'success');
                    location.reload(); // Полная перезагрузка страницы
                }
                // Если задача завершена с ошибкой
                else if (data.result.status === 'failure') {
                    clearInterval(interval);
                    alert('Ошибка при выполнении задачи');
                }
                // Если задача всё ещё в процессе (PENDING), продолжаем проверку
                else if (data.result.status === 'pending') {
                    console.log('Задача в процессе...');
                }
            });
        }, 2000); // Проверка статуса задачи каждые 2 секунды
    }
</script>
