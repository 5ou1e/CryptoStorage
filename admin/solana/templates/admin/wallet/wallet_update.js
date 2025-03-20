    <script>
        // Логика обновления кошелька
        function updateWalletStats() {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Получение CSRF токена
            const updateWalletStatsUrl = "{% url 'admin:wallet_update_stats' wallet_id=wallet.wallet_id %}"; // Подставляем walletId

            fetch(updateWalletStatsUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    showNotification('Обновление поставлено в очередь!', 'success');
                    console.log(data.task_id);
                    checkStatsUpdateTaskStatus(data.task_id);
                }  else {
                    showNotification('Ошибка! Попробуйте снова.', 'error');
                }
            })
            .catch(error => {
                alert('Ошибка: ' + error);
            });
        }
        // Функция для замены __TASK_ID__ на реальный task_id
        function getUpdateTaskStatusUrl(taskId) {
            const url = "{% url 'admin:wallet_update_stats_task_status' wallet_id=wallet.wallet_id task_id='__TASK_ID__' %}";
            return url.replace('__TASK_ID__', taskId);
        }
        function checkStatsUpdateTaskStatus(taskId) {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Получение CSRF токена
            const interval = setInterval(function() {
                const updateWalletStatsTaskStatusUrl = getUpdateTaskStatusUrl(taskId);
                fetch(updateWalletStatsTaskStatusUrl, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'SUCCESS') {
                            clearInterval(interval);
                            // Здесь можно обновить страницу или элемент
                            location.reload(); // Полная перезагрузка страницы
                        } else if (data.status === 'FAILURE') {
                            clearInterval(interval);
                            alert('Ошибка при выполнении задачи');
                        }
                    });
            }, 2000); // Проверка каждые 2 секунды
        }
    </script>