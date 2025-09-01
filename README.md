**Food Forum** 
is a Django-based web application where users can share recipes, save their favorite dishes, build personal profiles, and interact with other cooking enthusiasts.



### Authentication & Profile
- User registration, login, and logout
- Profile page with:
  - Avatar (profile picture upload)
  - Email, nickname, reputation
  - Buttons for:
    - Editing profile
    - Changing password
    - Viewing saved recipes
    - Viewing own recipes

### Recipes
- Add a new recipe with ingredients and products
- View recipe detail page
- Save recipes ("Saved Recipes")
- View personal recipes ("My Recipes")
- Browse all recipes ("All Recipes")

### Interactions
- Like/dislike recipes


##  Tech Stack
- **Backend**: Django 5.2
- **Database**: SQLite (default, easy to switch to PostgreSQL)
- **Frontend**: HTML + Bootstrap
- **Auth**: Django built-in authentication system
- **Media**: Django Media for images (avatars, recipe photos)

---
## ⚙Installation & Run

1. Clone the repository:
```bash
git clone https://github.com/bohdankolisnyk04/food-forum.git
cd food-forum

2. Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows

3. Apply migrations:

python manage.py migrate


4. Run the development server:

python manage.py runserver
