from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator, MinLengthValidator


DECIMAL_QTY = {
    "max_digits": 10,
    "decimal_places": 2,
    "validators": [MinValueValidator(Decimal("0"))],
}

DECIMAL_MACRO = {
    "max_digits": 7,
    "decimal_places": 2,
    "validators": [MinValueValidator(Decimal("0"))],
}

class FoodForumUser(AbstractUser):
    nickname = models.CharField(
        max_length=30,
        unique=True,
        validators=[MinLengthValidator(2)],
    )
    bio = models.TextField(
        blank=True,
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text="Profile picture"
    )
    reputation = models.PositiveIntegerField(default=0)
    is_active_contributor = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="foodforum_users",
        blank=True,
        help_text="The groups this user belongs to."
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="foodforum_users_permissions",
        blank=True,
        help_text="Specific permissions for this user."
    )


    class Meta:
        verbose_name = "FoodForum User"
        verbose_name_plural = "FoodForum Users"

    def __str__(self):
        if self.nickname:
            return f"{self.nickname} ({self.username})"
        return self.username

    def increment_reputation(self, points=1):
        self.reputation += points
        self.save(update_fields=["reputation"])

    def decrement_reputation(self, points=1):
        self.reputation = max(0, self.reputation - points)
        self.save(update_fields=["reputation"])


class TimeTracker(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
    )

    unit = models.CharField(
        max_length=20,
        choices=[
            ("g", "grams"),
            ("ml", "milliliters"),
            ("pcs", "pieces"),
        ],
    )

    calories_per_100 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    protein_per_100 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    fat_per_100 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    density_g_per_ml = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    grams_per_piece = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
    )

    carbs_per_100 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.unit})"


class Recipe(TimeTracker):
    author = models.ForeignKey("forum.FoodForumUser", on_delete=models.CASCADE, related_name="recipes")
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)

    recipe_text = models.TextField()
    image = models.ImageField(
        upload_to="recipes/", blank=True, null=True,
    )
    time_minutes = models.PositiveIntegerField(default=0)
    servings = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title

    def nutrition_total(self):
        totals = {
            "protein": Decimal("0"),
            "fat": Decimal("0"),
            "carbs": Decimal("0"),
            "kcal": Decimal("0"),
        }

        for ingredient in self.ingredients.select_related("product").all():
            nutrition = ingredient.nutrition()
            totals["protein"] += nutrition["protein"]
            totals["fat"] += nutrition["fat"]
            totals["carbs"] += nutrition["carbs"]
            totals["kcal"] += nutrition["kcal"]

        for nutrient, value in totals.items():
            totals[nutrient] = round(value, 2)

        return totals

    def nutrition_per_serving(self):
        total_nutrition = self.nutrition_total()
        servings_count = max(self.servings, 1)

        nutrition_per_serving = {
            nutrient: round(value / servings_count, 2)
            for nutrient, value in total_nutrition.items()
        }

        return nutrition_per_serving

    def rating(self) -> int:
        total_score = self.reactions.aggregate(total=Sum("value"))["total"] or 0
        return int(total_score)

    def likes_count(self) -> int:
        return self.reactions.filter(value=Reaction.UPVOTE).count()

    def dislikes_count(self) -> int:
        return self.reactions.filter(value=Reaction.DOWNVOTE).count()

    def is_saved_by(self, user):
        if not user.is_authenticated:
            return False
        return self.saved_by.filter(user=user).exists()

    @classmethod
    def with_missing_products(cls, available_products):
        user_product_ids = {p.id if hasattr(p, "id") else p for p in available_products}

        recipes = cls.objects.prefetch_related("ingredients__product")

        results = []

        for recipe in recipes:
            recipe_product_ids = {ingredient.product.id for ingredient in recipe.ingredients.all()}
            missing_ids = recipe_product_ids - user_product_ids
            missing_products = [
                ingredient.product.name
                for ingredient in recipe.ingredients.all()
                if ingredient.product.id in missing_ids
            ]

            results.append({
                "recipe": recipe,
                "missing_products": missing_products,
                "missing_count": len(missing_products),
                "full_match": len(missing_products) == 0
            })

        results.sort(key=lambda r: (r["full_match"], -r["missing_count"]), reverse=True)

        return results


class RecipeIngredient(TimeTracker):
    UNIT_GRAM = "g"
    UNIT_MILLILITER = "ml"
    UNIT_PIECE = "pcs"

    UNIT_CHOICES = (
        (UNIT_GRAM, "grams"),
        (UNIT_MILLILITER, "milliliters"),
        (UNIT_PIECE, "pieces"),
    )

    recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        related_name="ingredients"
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.PROTECT,
        related_name="used_in"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Quantity in selected unit"
    )

    unit = models.CharField(
        max_length=3,
        choices=UNIT_CHOICES,
        default=UNIT_GRAM
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional note (e.g., 'chopped')"
    )

    class Meta:
        unique_together = (("recipe", "product"),)
        indexes = [
            models.Index(fields=["recipe", "product"]),
        ]

    def __str__(self):
        return f"{self.product.name}: {self.amount} {self.unit}"

    def as_grams(self) -> Decimal:
        quantity = Decimal(self.amount)

        if self.unit == self.UNIT_GRAM:
            return quantity

        if self.unit == self.UNIT_MILLILITER:
            density = self.product.density_g_per_ml or Decimal("1.0")
            return quantity * density

        if self.unit == self.UNIT_PIECE:
            if not self.product.grams_per_piece:
                raise ValueError(
                    f"Product '{self.product.name}' missing 'grams_per_piece' value"
                )
            return quantity * self.product.grams_per_piece

        return quantity

    def nutrition(self):
        grams = self.as_grams()
        factor = grams / Decimal("100")

        return {
            "protein": self.product.protein_per_100 * factor,
            "fat": self.product.fat_per_100 * factor,
            "carbs": self.product.carbs_per_100 * factor,
            "kcal": self.product.calories_per_100 * factor,
        }


class Reaction(TimeTracker):
    UPVOTE = 1
    DOWNVOTE = -1
    VALUE_CHOICES = (
        (UPVOTE, "Like"),
        (DOWNVOTE, "Dislike"),
    )

    user = models.ForeignKey("forum.FoodForumUser", on_delete=models.CASCADE, related_name="reactions")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="reactions")
    value = models.SmallIntegerField(choices=VALUE_CHOICES)

    class Meta:
        unique_together = (("user", "recipe"),)
        indexes = [
            models.Index(fields=["recipe"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.recipe_id}: {self.value}"


class SavedRecipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_recipes")
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe")
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user.nickname} saved {self.recipe.title}"
