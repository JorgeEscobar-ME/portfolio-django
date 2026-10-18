import re
from urllib.parse import parse_qs, urlsplit

from django.db import models
from django.urls import reverse


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PUBLISHED = "published", "Publicado"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.CharField(max_length=300)
    description = models.TextField()
    authors = models.CharField(max_length=300, blank=True, verbose_name="Autores")
    article_content = models.TextField(
        blank=True,
        verbose_name="Contenido del artículo",
        help_text="Escribe en Markdown. Usa $...$ para fórmulas en línea y $$...$$ para fórmulas en bloque.",
    )
    video_url = models.URLField(blank=True, verbose_name="Enlace del video")
    video_summary = models.TextField(blank=True, verbose_name="Resumen del video")
    main_results = models.TextField(blank=True, verbose_name="Resultados principales")
    conclusions = models.TextField(blank=True, verbose_name="Conclusiones")
    python_code = models.TextField(blank=True, verbose_name="Código Python")
    notebook_url = models.URLField(blank=True, verbose_name="Enlace a Google Colab")
    technologies = models.CharField(max_length=300, blank=True)
    repository_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PUBLISHED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-featured", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"slug": self.slug})

    @property
    def youtube_embed_url(self):
        if not self.video_url:
            return ""

        parsed_url = urlsplit(self.video_url)
        hostname = (parsed_url.hostname or "").lower()
        if hostname in {"youtu.be", "www.youtu.be"}:
            video_id = parsed_url.path.strip("/").split("/", maxsplit=1)[0]
        elif hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
            if parsed_url.path == "/watch":
                video_id = parse_qs(parsed_url.query).get("v", [""])[0]
            else:
                path_parts = parsed_url.path.strip("/").split("/")
                if len(path_parts) == 2 and path_parts[0] in {
                    "embed",
                    "live",
                    "shorts",
                }:
                    video_id = path_parts[1]
                else:
                    video_id = ""
        else:
            return ""

        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            return ""
        return f"https://www.youtube-nocookie.com/embed/{video_id}"