FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей проекта
COPY requirements.txt /app/
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь код приложения в контейнер
COPY . /app

# Команда для запуска приложения
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]