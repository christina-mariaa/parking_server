# Используем официальный образ Python
FROM python:3.10

# Отключаем буферизацию вывода Python, чтобы логи отображались сразу
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл requirements.txt в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . /app/

# Открываем порт 8000, на котором будет работать Django-сервер
EXPOSE 8000

# Запускаем миграции базы данных
CMD ["python", "manage.py", "migrate"]
# Запускаем Django-сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
