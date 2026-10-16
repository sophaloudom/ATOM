from django.urls import path
from django.contrib.auth import views as auth
from . import views
urlpatterns = [path('healthz/', views.health, name='health'), path('preferences/',views.preferences,name='preferences'), path('', views.dashboard, name='dashboard'), path('signup/',views.signup,name='signup'), path('login/',auth.LoginView.as_view(template_name='hub/auth.html'),name='login'), path('logout/',auth.LogoutView.as_view(),name='logout'), path('watch/<int:pk>/',views.watch,name='watch'), path('notifications/read/',views.read_notifications,name='read_notifications')]
