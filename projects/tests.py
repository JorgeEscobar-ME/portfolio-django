from django.test import TestCase
from django.urls import reverse

from .models import Project


class HomePageProjectTests(TestCase):
    def test_homepage_shows_only_three_latest_projects(self):
        projects = [
            Project.objects.create(
                title=f"Proyecto {index}",
                slug=f"proyecto-{index}",
                summary="Resumen",
                description="Descripción",
            )
            for index in range(1, 5)
        ]

        response = self.client.get(reverse("core:home"))

        self.assertEqual(
            list(response.context["recent_projects"]),
            [projects[3], projects[2], projects[1]],
        )
