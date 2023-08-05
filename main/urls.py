from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('accounts/signup/', views.signup, name='user_signup'),
    path('', views.player_info, name='main')
]