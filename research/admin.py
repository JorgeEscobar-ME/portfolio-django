from django import forms
from django.contrib import admin

from .models import ResearchItem


class ResearchItemAdminForm(forms.ModelForm):
    class Meta:
        model = ResearchItem
        fields = "__all__"
        widgets = {
            "content": forms.Textarea(attrs={"rows": 30}),
        }
        help_texts = {
            "content": (
                "Escribe en Markdown. Las imágenes se centran y limitan "
                "automáticamente (máximo 900 px). Para cambiar el ancho de cada "
                "imagen, selecciónala y usa el botón «Tamaño de imagen»."
            ),
        }


@admin.register(ResearchItem)
class ResearchItemAdmin(admin.ModelAdmin):
    form = ResearchItemAdminForm
    list_display = ("title", "topic", "publication", "year", "doi")
    list_filter = ("topic", "year")
    search_fields = ("title", "abstract", "content", "authors", "publication", "doi", "keywords")
    prepopulated_fields = {"slug": ("title",)}

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.css",
                "core/markdown-image-size.css",
            ),
        }
        js = (
            "https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.js",
            "core/markdown-image-size-dialog.js",
            "blog/admin-post-editor-image-size.js",
        )