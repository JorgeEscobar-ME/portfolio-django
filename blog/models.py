from django.db import models
from django.urls import reverse


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PUBLISHED = "published", "Publicado"

    class Theme(models.TextChoices):
        LIFE = "life", "Vida cotidiana"
        SCIENCE_OPINION = "science-opinion", "Opinión sobre ciencia"
        MATHEMATICS = "mathematics", "Matemáticas"
        EDUCATION = "education", "Educación"
        OTHER = "other", "Otros temas"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    theme = models.CharField(
        max_length=20,
        choices=Theme.choices,
        default=Theme.OTHER,
        verbose_name="Tema",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    highlighted = models.BooleanField(default=False, verbose_name="Destacada")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})