import tempfile
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ResearchItem


class ResearchItemTests(TestCase):
    def make_item(self, **overrides):
        values = {
            "title": "Investigación de prueba",
            "slug": "investigacion-de-prueba",
            "topic": ResearchItem.Topic.MATHEMATICS,
            "abstract": "Resumen de prueba.",
        }
        values.update(overrides)
        return ResearchItem.objects.create(**values)

    def test_detail_renders_markdown_math_code_and_publication_metadata(self):
        item = self.make_item(
            content=(
                "Un resultado con $x^2$.\n\n"
                "$$\ny = mx + b\n$$\n\n"
                "```python\nprint('hola')\n```"
            ),
            authors="Escobar, J. A.",
            publication="Revista de prueba",
            year=2026,
            doi="10.1234/example",
            keywords="matemáticas, educación",
            pdf_url="https://example.com/paper.pdf",
        )

        response = self.client.get(item.get_absolute_url())
        page = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn(r"\(x^2\)", page)
        self.assertIn(r"\[" + "\ny = mx + b\n" + r"\]", page)
        self.assertIn('class="language-python"', page)
        self.assertContains(response, "Escobar, J. A.")
        self.assertContains(response, "10.1234/example")
        self.assertContains(response, "Descargar BibTeX")
        self.assertContains(response, "Cita APA")

    def test_bibtex_and_apa_citations_download(self):
        item = self.make_item(
            authors="Escobar, J. A.",
            publication="Revista de prueba",
            year=2026,
            doi="10.1234/example",
        )

        bibtex_response = self.client.get(
            reverse("research:citation", args=[item.slug, "bibtex"])
        )
        apa_response = self.client.get(
            reverse("research:citation", args=[item.slug, "apa"])
        )

        self.assertEqual(bibtex_response.status_code, 200)
        self.assertIn(b"@article{investigacion-de-prueba", bibtex_response.content)
        self.assertIn(b"doi = {10.1234/example}", bibtex_response.content)
        self.assertIn(b"url = {https://doi.org/10.1234/example}", bibtex_response.content)
        self.assertIn(b"Escobar, J. A. (2026). Investigaci", apa_response.content)
        self.assertEqual(
            self.client.get(
                reverse("research:citation", args=[item.slug, "invalid"])
            ).status_code,
            404,
        )

    def test_uploaded_pdf_downloads_as_attachment(self):
        with tempfile.TemporaryDirectory() as media_directory:
            with override_settings(MEDIA_ROOT=Path(media_directory)):
                item = self.make_item(
                    pdf_file=SimpleUploadedFile(
                        "articulo.pdf",
                        b"%PDF-1.4\ncontenido",
                        content_type="application/pdf",
                    )
                )

                response = self.client.get(reverse("research:pdf", args=[item.slug]))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "application/pdf")
                self.assertIn("attachment", response["Content-Disposition"])
                self.assertEqual(b"".join(response.streaming_content), b"%PDF-1.4\ncontenido")

    def test_upload_rejects_non_pdf_content(self):
        item = self.make_item()
        item.pdf_file = SimpleUploadedFile(
            "not-a-pdf.pdf",
            b"not a PDF",
            content_type="application/pdf",
        )

        with self.assertRaisesMessage(ValidationError, "no parece ser un PDF válido"):
            item.full_clean()

    def test_homepage_research_cards_show_publication_year(self):
        self.make_item(year=2024)

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "2024")

    def test_homepage_shows_only_three_most_recent_research_items(self):
        items = [
            self.make_item(
                title=f"Investigación {year}",
                slug=f"investigacion-{year}",
                year=year,
            )
            for year in (2022, 2023, 2024, 2025)
        ]

        response = self.client.get(reverse("core:home"))

        self.assertEqual(
            list(response.context["recent_research"]),
            [items[3], items[2], items[1]],
        )
