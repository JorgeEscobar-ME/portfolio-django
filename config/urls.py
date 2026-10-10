from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("blog/", include("blog.urls")),
    path("investigacion/", include("research.urls")),
    path("proyectos/", include("projects.urls")),
]