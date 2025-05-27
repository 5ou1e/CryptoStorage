from celery import Celery

from src.settings import config

app = Celery("core")

app.conf.broker_url = config.celery.broker_url
app.conf.result_backend = config.celery.result_backend

# Автоматическое обнаружение задач
app.autodiscover_tasks(packages=["src.infra.celery.tasks"])

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
