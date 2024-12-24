DUBLICAT_USER = 'Вы уже подписаны на этого пользователя!'
SELF_FOLLOW = 'Вы не можете подписаться на самого себя!'
RECIPE_IN_FAVORITE = 'Вы уже добавили рецепт в избранное.'
INGREDIENT_MIN_AMOUNT_ERROR = (
    'Количество ингредиентов не может быть меньше {min_value}!'
)
INGREDIENT_DUBLICATE_ERROR = 'Ингредиенты не могут повторяться!'
COOKING_TIME_MIN_ERROR = (
    'Время приготовления не может быть меньше одной минуты!'
)
TAG_ERROR = 'Рецепт не может быть без тегов!'
TAG_UNIQUE_ERROR = 'Теги должны быть уникальными!'
ALREADY_BUY = 'Вы уже добавили рецепт в список покупок.'
LENG_MAX = 200
MAX_LENG = 32
MAX_NUMBER_OF_CHARACTERS = f'Количество символов не более {LENG_MAX}.'
LEN_RECIPE_NAME = 256
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000
INGREDIENT_MIN_AMOUNT = 1
MIN_AMOUNT = 1
USERNAME_REGEX = r'[\w\.@+-]+'
NOT_ALLOWED_CHAR_MSG = ('{chars} недопустимые символы '
                        'в имени пользователя {username}.')

NOT_ALLOWED_ME = ('Нельзя создать пользователя с '
                  'именем: << {username} >> - это имя запрещено!')

LENG_DATA_USER = 150
LIMITED_NUMBER_OF_CHARACTERS = f'Набор символов не более {LENG_DATA_USER}'
LENG_EMAIL = 254
MAX_AMOUNT = 32000
PAGINATION_NUMBER = 6
