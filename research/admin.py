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
            ),
        }
        js = (
            "https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.js",
            "blog/admin-post-editor.js",
        )