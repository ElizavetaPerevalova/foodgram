import csv
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from api.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv-файла в базу данных (модель Ингредиенты)'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Path to file')

    def handle(self, *args, **options):
        success_count = 0
        with open(
                f'{settings.BASE_DIR}/data/ingredients.csv',
                'r',
                encoding='utf-8',
        ) as csv_file:
            reader = csv.reader(csv_file)

            for row in reader:
                name_csv = 0
                unit_csv = 1
                try:
                    obj, created = Ingredient.objects.get_or_create(
                        name=row[name_csv],
                        measurement_unit=row[unit_csv],
                    )
                    if created:
                        success_count += 1
                except Exception as error:
                    logging.exception(f'Ошибка в строке {row}: {error}')
# class Command(BaseCommand):

#     PATH_DATA, FILE_NAME = 'data', 'ingredients.csv'

#     PATH = settings.BASE_DIR.parent.joinpath(PATH_DATA)

#     FIELD_NAMES = ('name', 'measurement_unit')

#     help = f'''Populates Database with the Data from csv-File Located within
# {PATH_DATA}'''

#     def handle(self, *args, **options) -> None:

#         with open(self.PATH.joinpath(self.FILE_NAME), encoding='utf8') as file:
#             reader = csv.DictReader(file, fieldnames=self.FIELD_NAMES)
#             Ingredient.objects.bulk_create(Ingredient(**_) for _ in reader)

#         self.stdout.write(
#             self.style.SUCCESS(
#                 f'''Successfully Populated Database with the Data from
# csv-File Located within {self.PATH_DATA}'''
#             )
#         )
