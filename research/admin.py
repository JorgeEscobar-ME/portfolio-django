from django.contrib import admin

from .models import ResearchItem


@admin.register(ResearchItem)
class ResearchItemAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "publication", "year")
    list_filter = ("topic", "year")
    search_fields = ("title", "abstract", "authors", "publication")
    prepopulated_fields = {"slug": ("title",)}