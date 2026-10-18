from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="list"),
    path("<slug:slug>/imagen/", views.project_cover, name="cover"),
    path("<slug:slug>/", views.project_detail, name="detail"),
]