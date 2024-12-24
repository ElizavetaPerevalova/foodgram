import os
import sys

# Путь к проекту
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Установка переменной окружения с настройками
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

from django.core.wsgi import get_wsgi_application

# Экспортируем WSGI-приложение
application = get_wsgi_application()
