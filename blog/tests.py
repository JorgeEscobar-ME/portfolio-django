from django.test import TestCase
from django.urls import reverse

from .models import Post


class PostVisibilityTests(TestCase):
    def test_published_post_is_visible(self):
        post = Post.objects.create(
            title="Publicación de prueba",
            slug="publicacion-de-prueba",
            content="Contenido",
            status=Post.Status.PUBLISHED,
        )

        response = self.client.get(reverse("blog:list"))
        self.assertContains(response, post.title)
        self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 200)

    def test_draft_is_not_visible(self):
        post = Post.objects.create(
            title="Borrador privado",
            slug="borrador-privado",
            content="Contenido",
        )

        response = self.client.get(reverse("blog:list"))
        self.assertNotContains(response, post.title)
        self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 404)


class HomePageTests(TestCase):
    def test_home_page_loads_without_content(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)