from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("blog/", include("blog.urls")),
    path("investigacion/", include("research.urls")),
    path("proyectos/", include("projects.urls")),
    path("cv/", include("cv.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)