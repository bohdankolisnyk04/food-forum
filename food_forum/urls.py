from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('forum/', include('forum.urls', namespace='forum')),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', RedirectView.as_view(url='/forum/', permanent=False)),
]
