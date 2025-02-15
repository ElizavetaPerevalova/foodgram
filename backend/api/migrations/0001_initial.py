# Generated by Django 3.2.3 on 2025-02-14 06:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favourites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранные',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Количество символов не более 200.', max_length=200, unique=True, verbose_name='Название')),
                ('measurement_unit', models.CharField(help_text='Количество символов не более 200.', max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IngredientInRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, message='Количество ингредиентов не может быть меньше {min_value}!')], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Количество ингредиента',
                'verbose_name_plural': 'Количество ингредиентов',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название рецепта, не более 256 символов.', max_length=256, verbose_name='Название рецепта')),
                ('image', models.ImageField(help_text='Картинка рецепта.', upload_to='api/recipes/', verbose_name='Картинка')),
                ('text', models.TextField(help_text='Описание рецепта.', verbose_name='Описание рецепта')),
                ('cooking_time', models.PositiveIntegerField(help_text='Время приготовления в минутах от 1 до 32000.', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32000)], verbose_name='Время приготовления в минутах')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название тега, не более 32 символов.', max_length=32, unique=True, verbose_name='Название тега')),
                ('slug', models.SlugField(help_text='Слаг тега, не более 32 символов.', max_length=32, unique=True, verbose_name='Слаг тега')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_shopping_list', to='api.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'список покупок',
                'verbose_name_plural': 'Список покупок',
            },
        ),
    ]
