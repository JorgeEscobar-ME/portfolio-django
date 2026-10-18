from django import forms
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone

from .backup import (
    BackupValidationError,
    create_backup,
    inspect_backup,
    restore_backup,
)
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
            "summary": (
                "Admite Markdown, listas, negritas, enlaces e imágenes. Las imágenes "
                "se centran y limitan automáticamente (máximo 900 px); selecciona "
                "una imagen y usa el botón "
                "«Tamaño de imagen» para ajustar su ancho."
            ),
            "description": (
                "Admite Markdown, listas, negritas, enlaces e imágenes. Las imágenes "
                "se centran y limitan automáticamente (máximo 900 px); selecciona "
                "una imagen y usa el botón "
                "«Tamaño de imagen» para ajustar su ancho."
            ),
            "details": (
                "Admite Markdown, listas, negritas, enlaces e imágenes. Las imágenes "
                "se centran y limitan automáticamente (máximo 900 px); selecciona "
                "una imagen y usa el botón "
                "«Tamaño de imagen» para ajustar su ancho."
            ),
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
                "core/markdown-image-size.css",
            ),
        }
        js = (
            "https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.js",
            "core/markdown-image-size-dialog.js",
            "cv/admin-cv-editor.js",
        )


@admin.register(CVProfile)
class CVProfileAdmin(CVMarkdownEditorAdminMixin, admin.ModelAdmin):
    form = CVProfileForm
    fields = ("summary",)
    change_form_template = "admin/cv/cvprofile/change_form.html"

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not CVProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return (
            super().has_delete_permission(request, obj)
            and obj is not None
            and obj.pk != 1
        )

    def get_urls(self):
        custom_urls = [
            path(
                "backup/",
                self.admin_site.admin_view(self.backup_view),
                name="cv_cvprofile_backup_database",
            ),
            path(
                "restore/",
                self.admin_site.admin_view(self.restore_view),
                name="cv_cvprofile_restore_database",
            ),
        ]
        return custom_urls + super().get_urls()

    def backup_view(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied
        try:
            backup = create_backup()
        except BackupValidationError as error:
            messages.error(request, str(error))
            return HttpResponseRedirect(reverse("admin:index"))
        timestamp = timezone.now().strftime("%Y%m%d-%H%M%S")
        return FileResponse(
            backup,
            as_attachment=True,
            filename=f"portfolio-backup-{timestamp}.zip",
            content_type="application/zip",
        )

    def restore_view(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Restaurar copia de seguridad",
            "errors": [],
        }
        if request.method == "POST":
            uploaded_file = request.FILES.get("backup_file")
            if request.POST.get("confirm_restore") != "RESTORE":
                context["errors"].append(
                    'Escribe RESTORE para confirmar que los datos actuales serán reemplazados.'
                )
            elif uploaded_file is None:
                context["errors"].append("Selecciona un archivo de copia de seguridad.")
            else:
                try:
                    fixture, media_files = inspect_backup(uploaded_file)
                    restore_backup(fixture, media_files)
                except BackupValidationError as error:
                    context["errors"].append(str(error))
                else:
                    messages.success(
                        request,
                        "La copia se restauró. Vuelve a iniciar sesión si se te solicita.",
                    )
                    return HttpResponseRedirect(reverse("admin:index"))
        return render(request, "admin/cv/backup_restore.html", context)


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
