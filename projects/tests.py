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


class ProjectDetailTests(TestCase):
    def test_project_detail_renders_markdown_latex_and_sanitizes_html(self):
        project = Project.objects.create(
            title="Proyecto con artículo",
            slug="proyecto-con-articulo",
            summary="Resumen del proyecto",
            description="Descripción",
            article_content=(
                "# Método\n\n"
                "Una ecuación $x_1$.\n\n"
                "$$\n\\frac{a}{b}\n$$\n\n"
                '<img src=x onerror="alert(1)">'
            ),
        )

        response = self.client.get(project.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Método</h1>", html=True)
        self.assertIn(r"\(x_1\)", response.content.decode())
        self.assertIn(r"\frac{a}{b}", response.content.decode())
        self.assertNotIn("onerror", response.content.decode())

    def test_project_detail_embeds_only_valid_youtube_video_urls(self):
        project = Project.objects.create(
            title="Proyecto en video",
            slug="proyecto-en-video",
            summary="Resumen",
            description="Descripción",
            video_url="https://youtu.be/abcdefghijk",
            video_summary="Resumen preparado con IA",
            main_results="Resultado principal",
            conclusions="Conclusión",
        )

        response = self.client.get(project.get_absolute_url())

        self.assertContains(
            response,
            "https://www.youtube-nocookie.com/embed/abcdefghijk",
        )
        self.assertContains(response, 'sandbox="allow-scripts allow-same-origin allow-presentation"')
        self.assertContains(response, "Resumen preparado con IA")
        self.assertContains(response, "Resultado principal")
        self.assertContains(response, "Conclusión")

    def test_project_detail_displays_python_code_without_running_it(self):
        code = 'print("<script>alert(1)</script>")'
        project = Project.objects.create(
            title="Proyecto con Python",
            slug="proyecto-con-python",
            summary="Resumen",
            description="Descripción",
            python_code=code,
            notebook_url="https://colab.research.google.com/notebooks/intro.ipynb",
        )

        response = self.client.get(project.get_absolute_url())

        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, project.notebook_url)

    def test_draft_projects_are_not_visible_in_list_or_detail(self):
        project = Project.objects.create(
            title="Proyecto en borrador",
            slug="proyecto-en-borrador",
            summary="Resumen",
            description="Descripción",
            status=Project.Status.DRAFT,
        )

        list_response = self.client.get(reverse("projects:list"))
        detail_response = self.client.get(project.get_absolute_url())

        self.assertNotContains(list_response, project.title)
        self.assertEqual(detail_response.status_code, 404)

    def test_video_embed_is_restricted_to_supported_youtube_urls(self):
        project = Project.objects.create(
            title="Proyecto externo",
            slug="proyecto-externo",
            summary="Resumen",
            description="Descripción",
            video_url="https://example.com/embed/abcdefghijk",
        )

        self.assertEqual(project.youtube_embed_url, "")
