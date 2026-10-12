from django.contrib import admin
from django.utils.html import format_html

from .models import SiteProfile


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Presentación",
            {
                "fields": (
                    "name",
                    "portrait",
                    "portrait_preview",
                    "cv_photo",
                    "cv_photo_preview",
                    "home_image",
                    "home_image_preview",
                    "headline",
                    "biography",
                )
            },
        ),
        (
            "Contacto y perfiles",
            {
                "fields": (
                    "public_email",
                    "github_url",
                    "linkedin_url",
                    "orcid_url",
                    "google_scholar_url",
                    "cv_url",
                )
            },
        ),
    )
    readonly_fields = (
        "portrait_preview",
        "cv_photo_preview",
        "home_image_preview",
        "updated_at",
    )

    @admin.display(description="Vista previa")
    def portrait_preview(self, obj):
        if not obj or not obj.portrait:
            return "No hay una imagen cargada."
        return format_html(
            '<img src="{}" alt="" style="width: 96px; height: 96px; '
            'object-fit: cover; border-radius: 50%;">',
            obj.portrait_url,
        )

    @admin.display(description="Vista previa de imagen de portada")
    def home_image_preview(self, obj):
        if not obj or not obj.home_image:
            return "No hay una imagen cargada."
        return format_html(
            '<img src="{}" alt="" style="width: 240px; max-height: 160px; '
            'object-fit: cover; border-radius: 12px;">',
            obj.home_image_url,
        )

    @admin.display(description="Vista previa de foto del CV")
    def cv_photo_preview(self, obj):
        if not obj or not obj.cv_photo:
            return "No hay una foto cargada."
        return format_html(
            '<img src="{}" alt="" style="width: 120px; height: 150px; '
            'object-fit: cover; border-radius: 12px;">',
            obj.cv_photo_url,
        )

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not SiteProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return (
            super().has_delete_permission(request, obj)
            and obj is not None
            and obj.pk != 1
        )