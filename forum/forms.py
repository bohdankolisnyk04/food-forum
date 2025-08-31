from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import FoodForumUser, Product, Recipe



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = FoodForumUser
        fields = ("username", "nickname", "password1", "password2")


class RecipeForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label="Select products for this recipe"
    )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'recipe_text', 'image', 'time_minutes', 'servings', 'is_published']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо клас Bootstrap до полів
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ not in ['CheckboxInput', 'CheckboxSelectMultiple']:
                field.widget.attrs.update({'class': 'form-control'})


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'unit', 'calories_per_100', 'protein_per_100', 'fat_per_100', 'carbs_per_100', 'density_g_per_ml', 'grams_per_piece']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Add Product'))


class RecipeSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="Search by recipe name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter recipe name...'})
    )
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Filter by products"
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = FoodForumUser
        fields = ['nickname', 'bio', 'avatar']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
