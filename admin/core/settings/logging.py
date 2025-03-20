

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # 'file': {
        #     'level': 'DEBUG',
        #     'class': 'logging.FileHandler',
        #     'filename': 'celery_tasks.log',
        #     'formatter': 'verbose',
        # },
    },
    'loggers': {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        'django.db.backends': {
            'level': 'DEBUG',  # Установите уровень логирования
            'handlers': ['console'],
        },
    },
}
