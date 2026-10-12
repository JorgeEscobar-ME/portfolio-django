from django.db import models
from django.urls import reverse


class SiteProfile(models.Model):
    name = models.CharField(max_length=160)
    portrait = models.ImageField(
        upload_to="profile/",
        blank=True,
        help_text="Idealmente cuadrada; se recorta automáticamente en la barra superior.",
    )
    cv_photo = models.ImageField(
        "foto para el CV",
        upload_to="profile/",
        blank=True,
        help_text="Foto que aparecerá en el currículum; se recomienda una imagen vertical.",
    )
    home_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        help_text="Imagen horizontal para la portada, junto a tu presentación.",
    )
    headline = models.CharField(max_length=240, blank=True)
    biography = models.TextField(blank=True)
    public_email = models.EmailField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    orcid_url = models.URLField(blank=True)
    google_scholar_url = models.URLField(blank=True)
    cv_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "perfil del portafolio"
        verbose_name_plural = "perfil del portafolio"

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def portrait_url(self):
        return reverse("core:portrait")

    @property
    def home_image_url(self):
        return reverse("core:home_image")

    @property
    def cv_photo_url(self):
        return reverse("core:cv_photo")