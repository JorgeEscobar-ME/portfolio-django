from django import forms
from django.contrib import admin

from .models import Post


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        widgets = {
            "content": forms.Textarea(attrs={"rows": 30}),
        }
        help_texts = {
            "content": (
                "Escribe en Markdown. Usa $...$ para fórmulas en línea y "
                "$$...$$ para fórmulas en bloque."
            ),
        }


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "theme", "status", "highlighted", "published_at", "updated_at")
    list_filter = ("status", "theme", "highlighted")
    search_fields = ("title", "excerpt", "content")
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