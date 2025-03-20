
# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем зависимости для сборки (например, libpq-dev для PostgreSQL)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt requirements.txt

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения в контейнер
COPY . /app

# Указываем команду по умолчанию (опционально)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]