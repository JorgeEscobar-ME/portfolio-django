from datetime import datetime, timezone

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Post


class PostVisibilityTests(TestCase):
    def test_admin_content_editor_loads_image_size_tool(self):
        from django.contrib.auth import get_user_model

        admin_user = get_user_model().objects.create_superuser(
            username="image-editor-admin",
            email="image-editor-admin@example.com",
            password="test-password",
        )
        post = Post.objects.create(
            title="Editor de imagen",
            slug="editor-de-imagen",
            content="Contenido",
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
                reverse("admin:blog_post_change", args=[post.pk])
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "markdown-image-size-dialog.js")
        self.assertContains(response, "markdown-image-size.css")
        self.assertContains(response, "admin-post-editor-image-size.js")

    def test_blog_list_filters_published_posts_by_theme(self):
        science_post = Post.objects.create(
            title="Opinión sobre ciencia",
            slug="opinion-sobre-ciencia",
            content="Contenido",
            status=Post.Status.PUBLISHED,
            theme=Post.Theme.SCIENCE_OPINION,
        )
        Post.objects.create(
            title="Un día cotidiano",
            slug="un-dia-cotidiano",
            content="Contenido",
            status=Post.Status.PUBLISHED,
            theme=Post.Theme.LIFE,
        )
        Post.objects.create(
            title="Borrador científico",
            slug="borrador-cientifico",
            content="Contenido",
            theme=Post.Theme.SCIENCE_OPINION,
        )

        response = self.client.get(
            reverse("blog:list"),
            {"tema": Post.Theme.SCIENCE_OPINION},
        )

        self.assertContains(response, science_post.title)
        self.assertNotContains(response, "Un día cotidiano")
        self.assertNotContains(response, "Borrador científico")
        self.assertEqual(response.context["selected_theme"], Post.Theme.SCIENCE_OPINION)
        self.assertContains(response, "Vida cotidiana")
        self.assertContains(response, "Opinión sobre ciencia")

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

    def test_post_detail_renders_markdown_and_preserves_math_safely(self):
        post = Post.objects.create(
            title="Contenido con formato",
            slug="contenido-con-formato",
            content=(
                "# Encabezado\n\n"
                "Texto **importante** y fórmula $x_1$.\n\n"
                "$$\n\\frac{a}{b}\n$$\n\n"
                '<img src=x onerror="alert(1)">'
            ),
            status=Post.Status.PUBLISHED,
        )

        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Encabezado</h1>", html=True)
        self.assertContains(response, "<strong>importante</strong>", html=True)
        rendered_page = response.content.decode()
        self.assertIn(r"\(x_1\)", rendered_page)
        self.assertIn('class="math-display"', rendered_page)
        self.assertIn(r"\frac{a}{b}", rendered_page)
        self.assertNotIn("onerror", rendered_page)

    def test_post_detail_preserves_plain_text_line_breaks(self):
        post = Post.objects.create(
            title="Texto con saltos",
            slug="texto-con-saltos",
            content="Primera línea\nSegunda línea",
            status=Post.Status.PUBLISHED,
        )

        response = self.client.get(post.get_absolute_url())

        self.assertContains(response, "Primera línea<br>")
        self.assertContains(response, "Segunda línea")

    def test_post_images_are_rendered_with_safe_optional_width(self):
        post = Post.objects.create(
            title="Publicación con imágenes",
            slug="publicacion-con-imagenes",
            content=(
                "![Imagen válida](https://example.com/valid.png){ width=480 }\n\n"
                "![Imagen demasiado ancha](https://example.com/large.png){ width=1200 }"
            ),
            status=Post.Status.PUBLISHED,
        )

        response = self.client.get(post.get_absolute_url())
        page = response.content.decode()

        self.assertContains(
            response,
            '<img alt="Imagen válida" src="https://example.com/valid.png" width="480">',
            html=True,
        )
        self.assertContains(response, '<img alt="Imagen demasiado ancha" src="https://example.com/large.png">', html=True)
        self.assertContains(response, ".post-content img")
        self.assertContains(response, "max-width: min(100%, 900px)")
        self.assertNotIn('width="1200"', page)

    def test_post_image_width_rejects_non_numeric_or_out_of_range_values(self):
        from .formatting import render_post_content

        rendered = render_post_content(
            "![Unsafe](https://example.com/image.png){ width=9000 }"
        )

        self.assertNotIn("width=", rendered)


class HomePageTests(TestCase):
    def test_home_page_loads_without_content(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)

    def test_highlighted_published_posts_appear_in_featured_panel(self):
        highlighted_post = Post.objects.create(
            title="Publicación destacada",
            slug="publicacion-destacada",
            excerpt="Una selección especial.",
            content="Contenido",
            status=Post.Status.PUBLISHED,
            highlighted=True,
        )
        Post.objects.create(
            title="Borrador destacado",
            slug="borrador-destacado",
            content="Contenido",
            highlighted=True,
        )
        Post.objects.create(
            title="Publicación normal",
            slug="publicacion-normal",
            content="Contenido",
            status=Post.Status.PUBLISHED,
        )

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, highlighted_post.title)
        self.assertContains(response, highlighted_post.excerpt)
        self.assertQuerySetEqual(
            response.context["highlighted_posts"],
            [highlighted_post],
        )

    def test_recent_posts_are_ordered_by_publication_date_and_show_date(self):
        older_post = Post.objects.create(
            title="Publicación anterior",
            slug="publicacion-anterior",
            content="Contenido",
            status=Post.Status.PUBLISHED,
            published_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        newest_post = Post.objects.create(
            title="Publicación más reciente",
            slug="publicacion-mas-reciente",
            content="Contenido",
            status=Post.Status.PUBLISHED,
            published_at=datetime(2026, 4, 12, 18, tzinfo=timezone.utc),
        )

        response = self.client.get(reverse("core:home"))

        self.assertEqual(
            list(response.context["recent_posts"]),
            [newest_post, older_post],
        )
        self.assertEqual(
            response.context["recent_posts"][0].display_date,
            newest_post.published_at,
        )
        self.assertContains(response, "2026-04-12")

    def test_homepage_shows_only_three_latest_published_posts(self):
        posts = [
            Post.objects.create(
                title=f"Publicación {index}",
                slug=f"publicacion-{index}",
                content="Contenido",
                status=Post.Status.PUBLISHED,
                published_at=datetime(2026, 1, index, tzinfo=timezone.utc),
            )
            for index in range(1, 5)
        ]

        response = self.client.get(reverse("core:home"))

        self.assertEqual(
            list(response.context["recent_posts"]),
            [posts[3], posts[2], posts[1]],
        )