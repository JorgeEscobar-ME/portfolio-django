from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("perfil/portrait/", views.portrait, name="portrait"),
    path("perfil/home-image/", views.home_image, name="home_image"),
    path("perfil/cv-photo/", views.cv_photo, name="cv_photo"),
]