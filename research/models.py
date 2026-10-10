from django.db import models
from django.urls import reverse


class ResearchItem(models.Model):
    class Topic(models.TextChoices):
        MATHEMATICS = "mathematics", "Matemáticas"
        EDUCATION = "education", "Educación"
        BOTH = "both", "Matemáticas y educación"

    title = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True)
    topic = models.CharField(max_length=20, choices=Topic.choices)
    abstract = models.TextField()
    authors = models.CharField(max_length=240, blank=True)
    publication = models.CharField(max_length=240, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    publication_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "title"]
        verbose_name = "trabajo de investigación"
        verbose_name_plural = "trabajos de investigación"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("research:detail", kwargs={"slug": self.slug})