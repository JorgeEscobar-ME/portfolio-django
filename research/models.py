from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


def validate_pdf_file(uploaded_file):
    if not uploaded_file.name.lower().endswith(".pdf"):
        raise ValidationError("El archivo debe tener extensión PDF.")

    position = uploaded_file.tell()
    signature = uploaded_file.read(5)
    uploaded_file.seek(position)
    if signature != b"%PDF-":
        raise ValidationError("El archivo seleccionado no parece ser un PDF válido.")


class ResearchItem(models.Model):
    class Topic(models.TextChoices):
        MATHEMATICS = "mathematics", "Matemáticas"
        EDUCATION = "education", "Educación"
        BOTH = "both", "Matemáticas y educación"

    title = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True)
    topic = models.CharField(max_length=20, choices=Topic.choices)
    abstract = models.TextField()
    content = models.TextField(
        blank=True,
        verbose_name="Contenido completo",
        help_text=(
            "Escribe en Markdown. Usa $...$ para fórmulas en línea y "
            "$$...$$ para fórmulas en bloque."
        ),
    )
    authors = models.CharField(max_length=240, blank=True)
    publication = models.CharField(max_length=240, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    publication_url = models.URLField(blank=True)
    doi = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="DOI",
        help_text="Ingresa el identificador DOI sin https://doi.org/.",
    )
    keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Palabras clave separadas por comas.",
    )
    pdf_file = models.FileField(
        upload_to="research/papers/%Y/",
        blank=True,
        validators=[validate_pdf_file],
        verbose_name="Archivo PDF",
    )
    pdf_url = models.URLField(
        blank=True,
        verbose_name="URL del PDF",
        help_text="Enlace alternativo al PDF publicado externamente.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "title"]
        verbose_name = "trabajo de investigación"
        verbose_name_plural = "trabajos de investigación"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("research:detail", kwargs={"slug": self.slug})