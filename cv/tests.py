from datetime import date
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from reportlab.platypus import ListFlowable

from core.models import SiteProfile

from .models import CVProfile, Certification, Education, Experience, ResearchProduct, Skill


class CVPageTests(TestCase):
    def setUp(self):
        self.profile, _ = SiteProfile.objects.update_or_create(
            pk=1,
            defaults={
                "name": "Jorge Alejandro Escobar Zúñiga",
                "headline": "Matemático y educador",
                "biography": "Perfil profesional de prueba.",
                "public_email": "jorge@example.com",
            },
        )
        self.cv_profile, _ = CVProfile.objects.update_or_create(
            pk=1,
            defaults={"summary": "Resumen editable para el currículum."},
        )
        Experience.objects.create(
            role="Docente",
            organization="Universidad de prueba",
            type=Experience.Type.TEACHING,
            dedication=Experience.Dedication.HOUR_CHAIR,
            start_date=date(2023, 1, 1),
            current=True,
            description=(
                "Diseño de cursos y acompañamiento estudiantil.\n\n"
                "- Planeación académica\n"
                "- Evaluación formativa"
            ),
        )
        Experience.objects.create(
            role="Analista de datos",
            organization="Centro de investigación",
            type=Experience.Type.PROFESSIONAL,
            dedication=Experience.Dedication.FULL_TIME,
            start_date=date(2022, 1, 1),
            end_date=date(2022, 12, 1),
        )
        Education.objects.create(
            degree="Maestría en Matemática",
            institution="Universidad Tecnológica de Pereira",
            current=True,
        )
        Skill.objects.create(
            name="Python",
            category=Skill.Category.TECHNICAL,
            proficiency="Avanzado",
        )
        ResearchProduct.objects.create(
            title="Modelación de sistemas dinámicos",
            product_type=ResearchProduct.Type.ARTICLE,
            venue="Revista de prueba",
            year=2024,
            authors="Jorge Escobar",
        )
        Certification.objects.create(
            title="Certificación de prueba",
            issuer="Institución de prueba",
        )

    def test_cv_page_displays_profile_and_resume_sections(self):
        response = self.client.get(reverse("cv:detail"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.name)
        self.assertContains(response, self.cv_profile.summary)
        self.assertContains(response, "Experiencia profesional")
        self.assertContains(response, "Experiencia docente")
        self.assertContains(response, "Docente")
        self.assertContains(response, "Hora cátedra")
        self.assertContains(response, "<ul>")
        self.assertContains(response, "Planeación académica")
        self.assertContains(response, "Tiempo completo")
        self.assertContains(response, "Analista de datos")
        self.assertContains(response, "Formación académica")
        self.assertContains(response, "Productos de investigación")
        self.assertContains(response, "Modelación de sistemas dinámicos")
        self.assertContains(response, "Habilidades")
        self.assertContains(response, "Python")
        self.assertContains(response, reverse("cv:download"))

    def test_pdf_download_returns_a_pdf_attachment(self):
        response = self.client.get(reverse("cv:download"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_markdown_lists_are_supported_in_pdf_content(self):
        from .formatting import markdown_to_reportlab_flowables
        from .views import _pdf_styles

        flowables = markdown_to_reportlab_flowables(
            "- Primer logro\n- Segundo logro",
            _pdf_styles(),
        )

        self.assertEqual(len(flowables), 1)
        self.assertIsInstance(flowables[0], ListFlowable)

    def test_cv_markdown_output_sanitizes_unsafe_html_and_links(self):
        from .formatting import render_cv_markdown

        rendered = render_cv_markdown(
            '<script>alert("unsafe")</script>\n\n[bad](javascript:alert(1))'
        )

        self.assertNotIn("<script>", rendered)
        self.assertNotIn('href="javascript:', rendered)

    def test_cv_markdown_renders_safely_sized_images_and_pdf_uses_alt_text(self):
        from .formatting import markdown_to_reportlab_flowables, render_cv_markdown
        from .views import _pdf_styles

        markdown_source = (
            "![Diagrama](https://example.com/diagram.png){ width=440 }"
        )
        rendered = render_cv_markdown(markdown_source)

        self.assertIn(
            '<img alt="Diagrama" src="https://example.com/diagram.png" width="440">',
            rendered,
        )
        self.assertEqual(
            markdown_to_reportlab_flowables(markdown_source, _pdf_styles())[0].getPlainText(),
            "Diagrama",
        )

    def test_admin_experience_form_loads_markdown_editor_for_description(self):
        admin_user = get_user_model().objects.create_superuser(
            username="cv-editor-admin",
            email="cv-editor-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)

        with override_settings(
            STORAGES={
                "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
                "staticfiles": {
                    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
                },
            }
        ):
            response = self.client.get(
                reverse(
                    "admin:cv_experience_change",
                    args=[Experience.objects.first().pk],
                )
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "markdown-editor")
        self.assertContains(response, "easymde.min.js")
        self.assertContains(response, "markdown-image-size-dialog.js")
        self.assertContains(response, "admin-cv-editor.js")

    def test_admin_can_download_and_restore_database_and_media_backup(self):
        admin_user = get_user_model().objects.create_superuser(
            username="backup-admin",
            email="backup-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                media_path = Path(media_root) / "profile" / "portrait.png"
                media_path.parent.mkdir(parents=True)
                media_path.write_bytes(b"backup-image")

                backup_response = self.client.get(
                    reverse("admin:cv_cvprofile_backup_database")
                )
                self.assertEqual(backup_response.status_code, 200)
                self.assertEqual(
                    backup_response["Content-Type"],
                    "application/zip",
                )
                backup_bytes = b"".join(backup_response.streaming_content)
                with ZipFile(BytesIO(backup_bytes)) as backup:
                    self.assertIn("data.json", backup.namelist())
                    self.assertIn("media/profile/portrait.png", backup.namelist())

                original_summary = self.cv_profile.summary
                self.cv_profile.summary = "Contenido que debe reemplazarse."
                self.cv_profile.save()
                media_path.write_bytes(b"current-image")
                uploaded_backup = SimpleUploadedFile(
                    "portfolio-backup.zip",
                    backup_bytes,
                    content_type="application/zip",
                )

                response = self.client.post(
                    reverse("admin:cv_cvprofile_restore_database"),
                    {
                        "backup_file": uploaded_backup,
                        "confirm_restore": "RESTORE",
                    },
                )

                self.assertEqual(response.status_code, 302)
                self.cv_profile.refresh_from_db()
                self.assertEqual(self.cv_profile.summary, original_summary)
                self.assertEqual(media_path.read_bytes(), b"backup-image")

    def test_restore_requires_explicit_confirmation_before_changing_data(self):
        admin_user = get_user_model().objects.create_superuser(
            username="restore-admin",
            email="restore-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("admin:cv_cvprofile_restore_database"),
            {"confirm_restore": "yes"},
        )

        self.assertEqual(response.status_code, 200)
        self.cv_profile.refresh_from_db()
        self.assertEqual(self.cv_profile.summary, "Resumen editable para el currículum.")

    def test_cv_profile_summary_is_managed_in_cv_admin(self):
        admin_user = get_user_model().objects.create_superuser(
            username="cv-admin",
            email="cv-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)

        with override_settings(
            STORAGES={
                "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
                "staticfiles": {
                    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
                },
            }
        ):
            change_response = self.client.get(
                reverse("admin:cv_cvprofile_change", args=[self.cv_profile.pk])
            )
        self.assertContains(change_response, "Descargar copia")
        self.assertContains(change_response, "Restaurar copia")

        response = self.client.post(
            reverse("admin:cv_cvprofile_change", args=[self.cv_profile.pk]),
            {"summary": "Actualizado desde el módulo de currículum."},
        )

        self.assertEqual(response.status_code, 302)
        self.cv_profile.refresh_from_db()
        self.assertEqual(
            self.cv_profile.summary,
            "Actualizado desde el módulo de currículum.",
        )
