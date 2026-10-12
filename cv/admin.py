from django import forms
from django.contrib import admin

from .models import (
    CVProfile,
    Certification,
    Education,
    Experience,
    ResearchProduct,
    Skill,
)


class CVMarkdownForm(forms.ModelForm):
    class Meta:
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 12, "class": "markdown-editor"}),
            "description": forms.Textarea(
                attrs={"rows": 12, "class": "markdown-editor"}
            ),
            "details": forms.Textarea(attrs={"rows": 12, "class": "markdown-editor"}),
        }
        help_texts = {
            "summary": "Admite Markdown, incluidas listas, negritas y enlaces.",
            "description": "Admite Markdown, incluidas listas, negritas y enlaces.",
            "details": "Admite Markdown, incluidas listas, negritas y enlaces.",
        }


class CVProfileForm(CVMarkdownForm):
    class Meta(CVMarkdownForm.Meta):
        model = CVProfile
        fields = "__all__"


class ExperienceForm(CVMarkdownForm):
    class Meta(CVMarkdownForm.Meta):
        model = Experience
        fields = "__all__"


class ResearchProductForm(CVMarkdownForm):
    class Meta(CVMarkdownForm.Meta):
        model = ResearchProduct
        fields = "__all__"


class EducationForm(CVMarkdownForm):
    class Meta(CVMarkdownForm.Meta):
        model = Education
        fields = "__all__"


class CVMarkdownEditorAdminMixin:
    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.css",
            ),
        }
        js = (
            "https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.js",
            "cv/admin-cv-editor.js",
        )


@admin.register(CVProfile)
class CVProfileAdmin(CVMarkdownEditorAdminMixin, admin.ModelAdmin):
    form = CVProfileForm
    fields = ("summary",)

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not CVProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return (
            super().has_delete_permission(request, obj)
            and obj is not None
            and obj.pk != 1
        )


@admin.register(Experience)
class ExperienceAdmin(CVMarkdownEditorAdminMixin, admin.ModelAdmin):
    form = ExperienceForm
    list_display = (
        "role",
        "organization",
        "type",
        "dedication",
        "start_date",
        "end_date",
        "current",
    )
    list_filter = ("type", "dedication", "current")
    search_fields = ("role", "organization", "description")
    ordering = ("display_order", "-start_date")


@admin.register(ResearchProduct)
class ResearchProductAdmin(CVMarkdownEditorAdminMixin, admin.ModelAdmin):
    form = ResearchProductForm
    list_display = ("title", "product_type", "venue", "year", "display_order")
    list_filter = ("product_type", "year")
    search_fields = ("title", "authors", "venue", "identifier", "description")
    ordering = ("display_order", "-year", "title")


@admin.register(Education)
class EducationAdmin(CVMarkdownEditorAdminMixin, admin.ModelAdmin):
    form = EducationForm
    list_display = ("degree", "institution", "start_date", "end_date", "current")
    list_filter = ("current",)
    search_fields = ("degree", "institution", "details")
    ordering = ("display_order", "-end_date")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "proficiency", "display_order")
    list_filter = ("category",)
    search_fields = ("name",)
    ordering = ("category", "display_order", "name")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("title", "issuer", "issued_on", "display_order")
    search_fields = ("title", "issuer")
    ordering = ("display_order", "-issued_on")
