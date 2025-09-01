from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, TemplateView, UpdateView

from forum.forms import CustomUserCreationForm, RecipeForm, ProfileUpdateForm
from forum.models import Recipe, FoodForumUser, Reaction, SavedRecipe, RecipeIngredient, Product


class RecipeListView(ListView):
    model = Recipe
    template_name = "forum/home.html"
    context_object_name = "recipes"

    def get_queryset(self):
        published_recipes = Recipe.objects.filter(is_published=True)
        recipes_with_rating = sorted(
            published_recipes,
            key=lambda r: r.rating(),
            reverse=True
        )
        return recipes_with_rating[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            saved_recipe_ids = self.request.user.saved_recipes.values_list('recipe_id', flat=True)
            context['saved_recipe_ids'] = set(saved_recipe_ids)
        else:
            context['saved_recipe_ids'] = set()
        return context


class RegisterView(CreateView):
    model = FoodForumUser
    form_class = CustomUserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "forum/recipe_detail.html"
    context_object_name = "recipe"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()
        if self.request.user.is_authenticated:
            context['is_saved'] = recipe.saved_by.filter(user=self.request.user).exists()
        else:
            context['is_saved'] = False
        return context


@login_required
def recipe_react(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":
        try:
            value = int(request.POST.get("value"))
        except (TypeError, ValueError):
            return redirect('forum:recipe-detail', pk=pk)

        if value not in [1, -1]:
            return redirect('forum:recipe-detail', pk=pk)

        # Правильний спосіб створення/оновлення
        reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            recipe=recipe,
            defaults={'value': value}  # обов’язково для нових записів
        )
        if not created:
            reaction.value = value
            reaction.save()

    return redirect('forum:recipe-detail', pk=pk)


@login_required
def toggle_saved(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    saved_entry, created = SavedRecipe.objects.get_or_create(user=request.user, recipe=recipe)

    if not created:
        saved_entry.delete()

    return redirect('forum:recipe-detail', pk=pk)


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'forum/recipe_create.html'
    success_url = reverse_lazy('forum:forum-home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class RecipeIngredientCreateView(LoginRequiredMixin, CreateView):
    model = RecipeIngredient
    fields = ['recipe', 'product', 'amount', 'unit', 'note']
    template_name = 'forum/ingredient_create.html'
    success_url = reverse_lazy('forum:forum-home')


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'unit', 'calories_per_100', 'protein_per_100', 'fat_per_100', 'carbs_per_100', 'density_g_per_ml', 'grams_per_piece']
    template_name = 'forum/product_create.html'
    success_url = reverse_lazy('forum:forum-home')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "forum/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            "user": user,
            "saved_recipes_count": user.saved_recipes.count(),
            "my_recipes_count": user.recipes.count(),
        })
        return context


class SavedRecipesView(LoginRequiredMixin, ListView):
    model = SavedRecipe
    template_name = "forum/saved_recipes.html"
    context_object_name = "saved_recipes"

    def get_queryset(self):
        return SavedRecipe.objects.filter(user=self.request.user).select_related('recipe')


class MyRecipesView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "forum/my_recipes.html"
    context_object_name = "recipes"
    paginate_by = 10

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user, is_published=True)


class AllRecipesView(ListView):
    model = Recipe
    template_name = "forum/all_recipes.html"
    context_object_name = "recipes"
    paginate_by = 12

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True).distinct()
        query = self.request.GET.get("q", "")
        product_ids = self.request.GET.getlist("products")

        if query:
            title_matches = queryset.filter(title__icontains=query)
        else:
            title_matches = queryset.none()

        if product_ids:
            product_matches = queryset.filter(ingredients__product__id__in=product_ids).distinct()
        else:
            product_matches = queryset.none()

        # Об’єднуємо результати
        if query and product_ids:
            # беремо унікальні рецепти, які відповідають хоча б одній умові
            combined = (title_matches | product_matches).distinct()
        elif query:
            combined = title_matches
        elif product_ids:
            combined = product_matches
        else:
            combined = queryset

        return combined

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['selected_products'] = [int(pid) for pid in self.request.GET.getlist("products")]
        context['search_query'] = self.request.GET.get("q", "")
        return context


class UserProfileView(DetailView):
    model = FoodForumUser
    template_name = "forum/user_profile.html"
    context_object_name = "profile_user"

    def get_object(self):
        return get_object_or_404(FoodForumUser, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_recipes'] = Recipe.objects.filter(author=self.get_object(), is_published=True)
        context['saved_recipes'] = self.get_object().saved_recipes.all()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = FoodForumUser
    form_class = ProfileUpdateForm
    template_name = "forum/profile_edit.html"
    success_url = reverse_lazy("forum:profile")

    def get_object(self):
        return self.request.user
