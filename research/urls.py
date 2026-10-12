from django.urls import path

from . import views

app_name = "research"

urlpatterns = [
    path("", views.research_list, name="list"),
    path("<slug:slug>/citation/<str:citation_type>/", views.research_citation, name="citation"),
    path("<slug:slug>/pdf/", views.research_pdf, name="pdf"),
    path("<slug:slug>/", views.research_detail, name="detail"),
]