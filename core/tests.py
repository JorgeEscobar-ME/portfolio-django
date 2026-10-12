from io import BytesIO
from os import environ
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import SiteProfile


class BootstrapSuperuserCommandTests(TestCase):
    credentials = {
        "DJANGO_SUPERUSER_USERNAME": "deployment-admin",
        "DJANGO_SUPERUSER_EMAIL": "deployment-admin@example.com",
        "DJANGO_SUPERUSER_PASSWORD": "A-strong-password-928!",
    }

    @override_settings(DEBUG=True)
    def test_creates_configured_superuser_only_once(self):
        with patch.dict(environ, self.credentials):
            call_command("bootstrap_superuser")
            call_command("bootstrap_superuser")

        user_model = get_user_model()
        self.assertEqual(
            user_model.objects.filter(username="deployment-admin").count(),
            1,
        )
        user = user_model.objects.get(username="deployment-admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(
            user.check_password(self.credentials["DJANGO_SUPERUSER_PASSWORD"])
        )

    def test_skips_when_no_credentials_are_configured(self):
        with patch.dict(environ, {}, clear=True):
            call_command("bootstrap_superuser")

        self.assertFalse(get_user_model().objects.exists())

    def test_rejects_incomplete_credentials(self):
        with patch.dict(
            environ,
            {"DJANGO_SUPERUSER_USERNAME": "deployment-admin"},
            clear=True,
        ):
            with self.assertRaises(CommandError):
                call_command("bootstrap_superuser")

        self.assertFalse(get_user_model().objects.exists())

    @override_settings(DEBUG=False)
    def test_requires_persistent_database_in_production(self):
        with patch.dict(environ, self.credentials):
            with self.assertRaisesMessage(
                CommandError,
                "requires a persistent database",
            ):
                call_command("bootstrap_superuser")

        self.assertFalse(get_user_model().objects.exists())


class HomePageProfileTests(TestCase):
    def test_home_page_displays_profile_and_public_links(self):
        SiteProfile.objects.update_or_create(
            pk=1,
            defaults={
                "name": "Jorge Alejandro Escobar Zúñiga",
                "headline": "Estudiante de Maestría en Matemática",
                "biography": "Me apasiona enseñar.",
                "public_email": "jorge@example.com",
                "github_url": "https://github.com/example",
            },
        )

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Jorge Alejandro Escobar Zúñiga")
        self.assertContains(response, "mailto:jorge@example.com")
        self.assertContains(response, "https://github.com/example")

    def test_home_page_still_loads_without_profile(self):
        SiteProfile.objects.all().delete()
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Matemáticas, educación e ingeniería")

    def test_admin_can_upload_portrait_and_it_appears_in_topbar(self):
        profile, _ = SiteProfile.objects.update_or_create(
            pk=1,
            defaults={"name": "Jorge Escobar"},
        )
        admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)

        image_buffer = BytesIO()
        Image.new("RGB", (32, 32), color="peachpuff").save(image_buffer, format="PNG")
        portrait_upload = SimpleUploadedFile(
            "portrait.png",
            image_buffer.getvalue(),
            content_type="image/png",
        )
        home_image_buffer = BytesIO()
        Image.new("RGB", (64, 40), color="coral").save(
            home_image_buffer,
            format="PNG",
        )
        home_image_upload = SimpleUploadedFile(
            "home-image.png",
            home_image_buffer.getvalue(),
            content_type="image/png",
        )
        cv_photo_buffer = BytesIO()
        Image.new("RGB", (40, 60), color="sandybrown").save(
            cv_photo_buffer,
            format="PNG",
        )
        cv_photo_upload = SimpleUploadedFile(
            "cv-photo.png",
            cv_photo_buffer.getvalue(),
            content_type="image/png",
        )

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse("admin:core_siteprofile_change", args=[profile.pk]),
                    {
                        "name": profile.name,
                        "portrait": portrait_upload,
                        "home_image": home_image_upload,
                        "cv_photo": cv_photo_upload,
                        "headline": "",
                        "biography": "",
                        "public_email": "",
                        "github_url": "",
                        "linkedin_url": "",
                        "orcid_url": "",
                        "google_scholar_url": "",
                        "cv_url": "",
                    },
                )
                self.assertEqual(response.status_code, 302)

                home_response = self.client.get(reverse("core:home"))
                self.assertContains(home_response, reverse("core:portrait"))
                self.assertContains(home_response, reverse("core:home_image"))

                cv_response = self.client.get(reverse("cv:detail"))
                self.assertContains(cv_response, reverse("core:cv_photo"))
                cv_pdf_response = self.client.get(reverse("cv:download"))
                self.assertEqual(cv_pdf_response.status_code, 200)
                self.assertTrue(cv_pdf_response.content.startswith(b"%PDF-"))

                portrait_response = self.client.get(reverse("core:portrait"))
                self.assertEqual(portrait_response.status_code, 200)
                self.assertEqual(portrait_response["Content-Type"], "image/png")
                self.assertEqual(
                    b"".join(portrait_response.streaming_content),
                    image_buffer.getvalue(),
                )
                home_image_response = self.client.get(reverse("core:home_image"))
                self.assertEqual(home_image_response.status_code, 200)
                self.assertEqual(home_image_response["Content-Type"], "image/png")
                self.assertEqual(
                    b"".join(home_image_response.streaming_content),
                    home_image_buffer.getvalue(),
                )
                cv_photo_response = self.client.get(reverse("core:cv_photo"))
                self.assertEqual(cv_photo_response.status_code, 200)
                self.assertEqual(cv_photo_response["Content-Type"], "image/png")
                self.assertEqual(
                    b"".join(cv_photo_response.streaming_content),
                    cv_photo_buffer.getvalue(),
                )