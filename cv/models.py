from django.db import models


class CVProfile(models.Model):
    summary = models.TextField(
        "perfil profesional",
        blank=True,
        help_text="Texto que aparece en la sección Perfil del currículum.",
    )

    class Meta:
        verbose_name = "perfil del currículum"
        verbose_name_plural = "perfil del currículum"

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Perfil del currículum"


class Experience(models.Model):
    class Type(models.TextChoices):
        PROFESSIONAL = "professional", "Experiencia profesional"
        TEACHING = "teaching", "Experiencia docente"

    class Dedication(models.TextChoices):
        FULL_TIME = "full_time", "Tiempo completo"
        PART_TIME = "part_time", "Medio tiempo"
        HOUR_CHAIR = "hour_chair", "Hora cátedra"
        CONTRACT = "contract", "Por prestación de servicios"
        FREELANCE = "freelance", "Independiente / freelance"
        INTERNSHIP = "internship", "Práctica / pasantía"
        OTHER = "other", "Otro"

    type = models.CharField(
        "tipo de experiencia",
        max_length=20,
        choices=Type.choices,
        default=Type.PROFESSIONAL,
    )
    role = models.CharField("cargo o rol", max_length=180)
    organization = models.CharField("organización", max_length=180)
    dedication = models.CharField(
        "dedicación",
        max_length=20,
        choices=Dedication.choices,
        blank=True,
    )
    location = models.CharField("ubicación", max_length=120, blank=True)
    start_date = models.DateField("fecha de inicio", null=True, blank=True)
    end_date = models.DateField("fecha de finalización", null=True, blank=True)
    current = models.BooleanField("actual", default=False)
    description = models.TextField("descripción y logros", blank=True)
    display_order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["-current", "-start_date", "display_order", "role"]
        verbose_name = "experiencia"
        verbose_name_plural = "experiencia"

    def __str__(self):
        return f"{self.role} — {self.organization}"


class ResearchProduct(models.Model):
    class Type(models.TextChoices):
        ARTICLE = "article", "Artículo científico"
        BOOK = "book", "Libro"
        CHAPTER = "chapter", "Capítulo de libro"
        CONFERENCE = "conference", "Ponencia / memoria de evento"
        THESIS = "thesis", "Tesis"
        DATASET = "dataset", "Conjunto de datos"
        SOFTWARE = "software", "Software"
        REPORT = "report", "Informe técnico"
        OTHER = "other", "Otro producto"

    title = models.CharField("título", max_length=240)
    product_type = models.CharField(
        "tipo de producto",
        max_length=20,
        choices=Type.choices,
        default=Type.ARTICLE,
    )
    authors = models.CharField("autores", max_length=400, blank=True)
    venue = models.CharField(
        "revista, editorial, evento o repositorio",
        max_length=240,
        blank=True,
    )
    year = models.PositiveSmallIntegerField("año", null=True, blank=True)
    identifier = models.CharField("DOI, ISBN u otro identificador", max_length=120, blank=True)
    product_url = models.URLField("enlace del producto", blank=True)
    description = models.TextField("descripción", blank=True)
    display_order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["-year", "display_order", "title"]
        verbose_name = "producto de investigación"
        verbose_name_plural = "productos de investigación"

    def __str__(self):
        return self.title


class Education(models.Model):
    degree = models.CharField("título o programa", max_length=180)
    institution = models.CharField("institución", max_length=180)
    location = models.CharField("ubicación", max_length=120, blank=True)
    start_date = models.DateField("fecha de inicio", null=True, blank=True)
    end_date = models.DateField("fecha de finalización", null=True, blank=True)
    current = models.BooleanField("en curso", default=False)
    details = models.TextField("detalles", blank=True)
    display_order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["-current", "-end_date", "-start_date", "display_order"]
        verbose_name = "formación académica"
        verbose_name_plural = "formación académica"

    def __str__(self):
        return f"{self.degree} — {self.institution}"


class Skill(models.Model):
    class Category(models.TextChoices):
        TECHNICAL = "technical", "Técnicas"
        LANGUAGES = "languages", "Idiomas"
        OTHER = "other", "Otras"

    name = models.CharField("habilidad", max_length=100)
    category = models.CharField(
        "categoría",
        max_length=20,
        choices=Category.choices,
        default=Category.TECHNICAL,
    )
    proficiency = models.CharField("nivel (opcional)", max_length=80, blank=True)
    display_order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["category", "display_order", "name"]
        verbose_name = "habilidad"
        verbose_name_plural = "habilidades"

    def __str__(self):
        return self.name


class Certification(models.Model):
    title = models.CharField("certificación", max_length=180)
    issuer = models.CharField("entidad emisora", max_length=180)
    issued_on = models.DateField("fecha de expedición", null=True, blank=True)
    credential_url = models.URLField("enlace de la credencial", blank=True)
    display_order = models.PositiveIntegerField("orden", default=0)

    class Meta:
        ordering = ["-issued_on", "display_order", "title"]
        verbose_name = "certificación"
        verbose_name_plural = "certificaciones"

    def __str__(self):
        return f"{self.title} — {self.issuer}"
