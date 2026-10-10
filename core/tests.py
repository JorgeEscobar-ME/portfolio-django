from django.test import TestCase
from django.urls import reverse

from .models import SiteProfile


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