import base64

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import (exceptions, fields, relations, serializers, status,
                            validators)
# from rest_framework.exceptions import PermissionDenied
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow, User
from .models import (Favourites, Ingredient, IngredientInRecipe, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from backend.constants import (ALREADY_BUY, COOKING_TIME_MIN_ERROR,
                               DUBLICAT_USER, INGREDIENT_DUBLICATE_ERROR,
                               INGREDIENT_MIN_AMOUNT_ERROR, RECIPE_IN_FAVORITE,
                               SELF_FOLLOW, TAG_ERROR, TAG_UNIQUE_ERROR)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'username',
                  'first_name', 'last_name', 'email',
                  'is_subscribed', 'avatar',)

    def get_is_subscribed(self, author):
        """Проверка подписки пользователей."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.follower.filter(author=author).exists())

    def create(self, validated_data: dict) -> User:
        """Создаёт нового пользователя с запрошенными полями.

    Args:
        validated_data (dict): Полученные проверенные данные.

    Returns:
        User: Созданный пользователь.
    """
        try:
            user = User(
                email=validated_data["email"],
                username=validated_data["username"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
            )
            user.set_password(validated_data["password"])
            user.save()
            return user
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        except Exception as e:
            raise ValueError(f"An error occurred while creating the user: {e}")


class FollowSerializer(UserSerializer):
    """Сериализатор вывода подписок текущего пользователя."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)
        read_only_fields = ('email', 'username', 'last_name', 'first_name',)

    def validate(self, data):
        """Проверяем наличие подписки у пользователя и отсекаем самого себя."""
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(user=user, author=author).exists():
            raise exceptions.ValidationError(
                detail=DUBLICAT_USER,
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise exceptions.ValidationError(
                detail=SELF_FOLLOW,
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        """Достаем количество рецептов."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Достаем рецептs."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара."""
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar",)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для вывода количества ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='ingredient'
    )

    name = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='name'
    )

    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = '__all__'


class UserListSerializer(
        serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.follower.filter(author=obj).exists()
            if user.is_authenticated
            else False
        )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed', 'avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для возврата списка рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True,
                                               required=True,
                                               source='ingredient_list')
    image = Base64ImageField()
    is_favorited = fields.SerializerMethodField(read_only=True)
    is_in_shopping_cart = fields.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation["is_favorited"] = representation.get(
    #         "is_favorited", False
    #     )
    #     representation["is_in_shopping_cart"] = representation.get(
    #         "is_in_shopping_cart", False
    #     )
    #     return representation

    def get_is_favorited(self, obj):
        """Проверка - находится ли рецепт в избранном."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favourites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Проверка - находится ли рецепт в списке покупок."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.shopping_list.filter(recipe=obj).exists())


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для ингредиента в рецепте."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class AddFavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецептов в избранное."""

    class Meta:
        model = Favourites
        fields = ('user', 'recipe')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favourites.objects.all(),
                fields=['user', 'recipe'],
                message=RECIPE_IN_FAVORITE
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeListSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="RecipeIngredient"
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, data):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favourites.objects.filter(
            user=request.user,
            recipe_id=data.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return obj.in_shopping_cart.filter(user=request.user).exists()


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Список покупок."""

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(), fields=("user", "recipe")
            )
        ]

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткий сериализатор рецепта."""
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FavoriteSerializer(serializers.ModelSerializer):
    """Избранное."""

    class Meta:
        model = Favourites
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Favourites.objects.all(), fields=("user", "recipe")
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class RecipeWriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для создание рецептов."""

    tags = relations.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                            many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'tags', 'author', 'ingredients',
                  'name', 'text', 'cooking_time')
        read_only_fields = ('author',)

    @transaction.atomic
    def create_bulk_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientInRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def validate(self, data):
        ingredients = data.get("ingredients")
        tags = data.get("tags")
        if not ingredients:
            raise serializers.ValidationError(
                "Необходимо добавить хотя бы один ингредиент."
            )
        if not tags:
            raise serializers.ValidationError(
                "Необходимо добавить хотя бы один тег."
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Теги должны быть уникальными.")
        if len(set(val["id"] for val in ingredients)) != len(ingredients):
            raise serializers.ValidationError(
                "Ингредиенты должны быть уникальными."
            )
        return data

    def add_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        request = self.context.get("request")
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        recipeingredient_set_data = validated_data.pop('recipeingredient_set')
        tags_data = validated_data.pop('tags')

        instance.ingredients.clear()
        instance.tags.clear()

        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                ingredient=pair['ingredient'],
                recipe=instance,
                amount=pair['amount']
            )
            for pair in recipeingredient_set_data
        )

        instance.tags.set(tags_data)

        return super().update(instance, validated_data)

    # def update(self, instance, validated_data):
    #     if instance.author != self.context["request"].user:
    #         raise PermissionDenied(
    #             "У вас нет прав на редактирование этого рецепта."
    #         )
    #     image = validated_data.get("image")
    #     if not image:
    #         raise serializers.ValidationError(
    #             'Поле "image" не может быть пустым.', code="invalid_image"
    #         )
    #     tags = validated_data.pop("tags")
    #     ingredients = validated_data.pop("ingredients")
    #     recipe = super().update(instance, validated_data)
    #     if tags:
    #         recipe.tags.clear()
    #         recipe.tags.set(tags)
    #     if ingredients:
    #         recipe.ingredients.clear()
    #         self.add_ingredients(ingredients, recipe)
    #     return recipe

    def validate_ingredients(self, value):
        """Проверяем ингредиенты в рецепте."""
        ingredients = self.initial_data.get('ingredients')
        if len(ingredients) <= 0:
            raise exceptions.ValidationError(
                {'ingredients': INGREDIENT_MIN_AMOUNT_ERROR}
            )
        ingredients_list = []
        for item in ingredients:
            if item['id'] in ingredients_list:
                raise exceptions.ValidationError(
                    {'ingredients': INGREDIENT_DUBLICATE_ERROR}
                )
            ingredients_list.append(item['id'])
            if int(item['amount']) <= 0:
                raise exceptions.ValidationError(
                    {'amount': INGREDIENT_MIN_AMOUNT_ERROR}
                )
        return value

    def validate_cooking_time(self, data):
        """Проверяем время приготовления рецепта."""
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                COOKING_TIME_MIN_ERROR
            )
        return data

    def validate_tags(self, value):
        """Проверяем на наличие уникального тега."""
        tags = value
        if not tags:
            raise exceptions.ValidationError(
                {'tags': TAG_ERROR}
            )
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise exceptions.ValidationError(
                    {'tags': TAG_UNIQUE_ERROR}
                )
            tags_list.append(tag)
        return value

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data


class AddShoppingListRecipeSerializer(AddFavoriteRecipeSerializer):
    """Сериализатор добавления рецептов в список покупок."""

    class Meta(AddFavoriteRecipeSerializer.Meta):
        model = ShoppingCart
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message=ALREADY_BUY
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class FavouriteAndShoppingCrtSerializer(serializers.ModelSerializer):
    """Сериализация избранного и корзины покупок."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
