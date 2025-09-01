from django.contrib import admin
from .models import FoodForumUser, Product, Recipe, RecipeIngredient, Reaction


@admin.register(FoodForumUser)
class FoodForumUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "nickname", "email", "reputation", "is_active_contributor", "is_staff")
    list_filter = ("is_active_contributor", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "nickname", "email")
    ordering = ("id",)
    readonly_fields = ("reputation",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("nickname", "first_name", "last_name", "email", "bio", "avatar")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Reputation", {"fields": ("reputation", "is_active_contributor")}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "calories_per_100", "protein_per_100", "fat_per_100", "carbs_per_100")
    search_fields = ("name",)
    list_filter = ("unit",)
    ordering = ("name",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ("product",)
    fields = ("product", "amount", "unit", "note")
    readonly_fields = ()


class ReactionInline(admin.TabularInline):
    model = Reaction
    extra = 0
    readonly_fields = ("user", "value")
    can_delete = False


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "time_minutes", "servings", "is_published")
    list_filter = ("is_published", "time_minutes", "servings")
    search_fields = ("title", "author__username", "author__nickname")
    ordering = ("-created_at",)
    autocomplete_fields = ("author",)
    inlines = [RecipeIngredientInline, ReactionInline]
    fieldsets = (
        (None, {"fields": ("title", "author", "description", "recipe_text", "image")}),
        ("Details", {"fields": ("time_minutes", "servings", "is_published")}),
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "product", "amount", "unit")
    list_filter = ("unit", "product")
    search_fields = ("recipe__title", "product__name")
    autocomplete_fields = ("recipe", "product")


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "value")
    list_filter = ("value",)
    search_fields = ("user__username", "user__nickname", "recipe__title")
    autocomplete_fields = ("user", "recipe")
    readonly_fields = ("user", "recipe", "value")
    can_delete = False
