from django.urls import path
from forum.views import RecipeListView, RegisterView, RecipeDetailView, recipe_react, toggle_saved, RecipeCreateView, \
    RecipeIngredientCreateView, ProductCreateView, ProfileView, SavedRecipesView, MyRecipesView, AllRecipesView, \
    UserProfileView, ProfileUpdateView

app_name = "forum"

urlpatterns = [
    path('', RecipeListView.as_view(), name="forum-home"),
    path("recipe/<int:pk>/", RecipeDetailView.as_view(), name="recipe-detail"),

    path("register/", RegisterView.as_view(), name="register"),
    path("recipe/<int:pk>/react/", recipe_react, name="recipe-react"),
    path('recipe/<int:pk>/toggle-save/', toggle_saved, name='toggle-saved'),
    path('recipe/add/', RecipeCreateView.as_view(), name='recipe-add'),
    path('ingredient/add/', RecipeIngredientCreateView.as_view(), name='ingredient-add'),
    path('product/add/', ProductCreateView.as_view(), name='product-add'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile-edit'),
    path('profile/saved/', SavedRecipesView.as_view(), name='saved-recipes'),
    path('profile/my-recipes/', MyRecipesView.as_view(), name='my-recipes'),

    path('all-recipes/', AllRecipesView.as_view(), name='all-recipes'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='user-profile'),
]

