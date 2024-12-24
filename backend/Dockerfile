# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в /app
WORKDIR /app

# Копируем все файлы из текущей директории в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт, на котором будет работать приложение
EXPOSE 8500

# Запускаем приложение с использованием Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8500", "foodgram.wsgi:application", " && tail -f /dev/null"]