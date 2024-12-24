# FROM python:3.9

# WORKDIR /app

# ENV PYTHONPATH=/app

# COPY requirements.txt /app/

# RUN pip install -r /app/requirements.txt --no-cache-dir

# COPY ./backend /app/

# CMD ["gunicorn", "--bind", "0.0.0.0:8500", "backend.wsgi:application"]
# Используем официальный образ Python
FROM python:3.9

# Устанавливаем рабочую директорию в /app
WORKDIR /app

# Копируем все файлы из текущей директории в контейнер
COPY . /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт, на котором будет работать приложение
EXPOSE 8500

# Запускаем приложение с использованием Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8500", "foodgram.wsgi:application"]