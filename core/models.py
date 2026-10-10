from django.db import models


class SiteProfile(models.Model):
    name = models.CharField(max_length=160)
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