from django.contrib import admin

from .models import SiteProfile


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Presentación", {"fields": ("name", "headline", "biography")}),
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
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not SiteProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return (
            super().has_delete_permission(request, obj)
            and obj is not None
            and obj.pk != 1
        )