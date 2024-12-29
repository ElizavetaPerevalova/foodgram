import csv
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from api.models import Ingredient


class Command(BaseCommand):
    PATH_DATA, FILE_NAME = 'data', 'ingredients.csv'

    PATH = settings.BASE_DIR.joinpath(PATH_DATA)

    FIELD_NAMES = ('name', 'measurement_unit')

    help = "Load ingredients from csv file"

    def handle(self, *args, **options):
        print("старт импорта ингредиентов")
        start_time = datetime.datetime.now()
        try:
            with open(
                "data/ingredients.csv",
                "r",
                encoding="utf-8",
            ) as file:
                if not file:
                    raise FileNotFoundError
                reader = csv.DictReader(file, fieldnames=self.FIELD_NAMES)
                for row in reader:
                    print(row)
                    Ingredient.objects.get_or_create(**row)
        except Exception as error:
            print(f"импорт завершен с ошибкой: {error}")
        print(f"импорт завершен за {datetime.datetime.now() - start_time}")
        self.stdout.write(self.style.SUCCESS("Импорт завершен"))
