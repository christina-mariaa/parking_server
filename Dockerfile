# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем зависимости для операционной системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем оставшиеся файлы проекта в контейнер
COPY . /app

# Открываем порт 8000 для Django-сервера
EXPOSE 8000

# Выполняем миграции, создаем суперпользователя и запускаем сервер
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
