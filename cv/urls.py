from django.urls import path

from . import views

app_name = "cv"

urlpatterns = [
    path("", views.cv_detail, name="detail"),
    path("descargar/", views.cv_pdf, name="download"),
]
