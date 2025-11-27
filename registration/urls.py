"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from registration import views
urlpatterns = [
    path("", views.home, name='home'),
    path("login/", views.login_view, name="login"),
    path("profile/", views.profile_view, name="profile"),
    path("logout/", views.logout_view, name="logout"),
    path('home/', views.home, name='home'),
    path("users/", views.users_list, name="users_list"),
    path("add-user/", views.add_user, name="add_user"),
    path("onspot/", views.onspot, name="onspot"),
    path("qr/", views.qr, name="qr"),
    path("qr_register/", views.qr_register, name="qr_register"),
    path("my_registrations/", views.my_registrations, name="my_registrations"),

]
