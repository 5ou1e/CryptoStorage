

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': 'db',  # Хост базы данных
                'port': '5432',  # Порт базы данных
                'user': 'admin',  # Имя пользователя
                'password': 'bestpassword123!',  # Пароль
                'database': 'crypto_storage',  # Имя базы данных
                'minsize': 1,  # Минимальное количество соединений в пуле
                'maxsize': 10,  # Максимальное количество соединений в пуле
            },
        },
    },
    'apps': {
        'models': {
            'models': ['solana.models.tortoise_models'],  # Укажите путь к вашим моделям
            'default_connection': 'default',
        },
    },
}
