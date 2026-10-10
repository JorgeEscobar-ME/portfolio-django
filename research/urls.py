from django.urls import path

from . import views

app_name = "research"

urlpatterns = [
    path("", views.research_list, name="list"),
    path("<slug:slug>/", views.research_detail, name="detail"),
]