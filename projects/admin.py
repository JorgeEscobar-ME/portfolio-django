from django import forms
from django.contrib import admin

from .models import Project


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "article_content": forms.Textarea(attrs={"rows": 30}),
            "python_code": forms.Textarea(attrs={"rows": 24}),
        }
        help_texts = {
            "video_summary": (
                "Pega aquí un resumen preparado por una herramienta de IA; "
                "el sitio no envía videos a un proveedor de IA."
            ),
            "main_results": "Describe los resultados principales del proyecto.",
            "conclusions": "Describe las conclusiones del proyecto.",
            "python_code": (
                "El código solo se muestra como texto y nunca se ejecuta en este sitio."
            ),
            "notebook_url": (
                "Enlaza un cuaderno de Google Colab si quieres permitir que se ejecute "
                "fuera de este sitio."
            ),
        }


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ("title", "status", "featured", "created_at")
    list_filter = ("status", "featured")
    search_fields = (
        "title",
        "summary",
        "description",
        "authors",
        "technologies",
        "video_summary",
    )
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)
    fieldsets = (
        (
            "Información del proyecto",
            {
                "fields": (
                    "title",
                    "slug",
                    "summary",
                    "description",
                    "authors",
                    "technologies",
                )
            },
        ),
        ("Artículo", {"fields": ("article_content",)}),
        (
            "Video",
            {
                "fields": (
                    "video_url",
                    "video_summary",
                    "main_results",
                    "conclusions",
                )
            },
        ),
        (
            "Código Python",
            {
                "fields": ("python_code", "notebook_url"),
            },
        ),
        (
            "Publicación y enlaces",
            {
                "fields": (
                    "repository_url",
                    "demo_url",
                    "status",
                    "featured",
                    "created_at",
                )
            },
        ),
    )

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.css",
            ),
        }
        js = (
            "https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.js",
            "projects/admin-project-editor.js",
        )