from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from blog.formatting import render_post_content

from .models import ResearchItem


def research_list(request):
    items = ResearchItem.objects.all()
    return render(request, "research/research_list.html", {"items": items})


def research_detail(request, slug):
    item = get_object_or_404(ResearchItem, slug=slug)
    return render(
        request,
        "research/research_detail.html",
        {
            "item": item,
            "rendered_content": render_post_content(item.content) if item.content else "",
        },
    )


def research_pdf(request, slug):
    item = get_object_or_404(ResearchItem, slug=slug)
    if not item.pdf_file or not item.pdf_file.storage.exists(item.pdf_file.name):
        raise Http404("No hay un PDF cargado para este trabajo.")

    return FileResponse(
        item.pdf_file.open("rb"),
        as_attachment=True,
        filename=f"{item.slug}.pdf",
        content_type="application/pdf",
    )


def research_citation(request, slug, citation_type):
    item = get_object_or_404(ResearchItem, slug=slug)
    doi_url = f"https://doi.org/{item.doi}" if item.doi else ""
    link = doi_url or item.publication_url
    citation_fields = [
        ("author", item.authors),
        ("year", str(item.year) if item.year else ""),
        ("title", item.title),
        ("journal", item.publication),
        ("doi", item.doi),
        ("url", link),
    ]

    if citation_type == "bibtex":
        bibtex_fields = [
            (name, value)
            for name, value in citation_fields
            if value and name != "url"
        ]
        if link:
            bibtex_fields.append(("url", link))
        fields = ",\n".join(
            f"  {name} = {{{_escape_bibtex(value)}}}"
            for name, value in bibtex_fields
        )
        citation = f"@article{{{item.slug},\n{fields}\n}}\n"
        filename = f"{item.slug}.bib"
    elif citation_type == "apa":
        citation = ""
        if item.authors:
            citation = item.authors.rstrip()
        if item.year:
            citation = f"{citation} ({item.year})" if citation else f"({item.year})"
            citation += ". "
        elif citation:
            if not citation.endswith((".", "?", "!")):
                citation += "."
            citation += " "
        citation += f"{item.title.rstrip('.')}."
        if item.publication:
            citation += f" {item.publication.rstrip('.')}."
        if link:
            citation += f" {link}"
        citation += "\n"
        filename = f"{item.slug}-citation.txt"
    else:
        raise Http404("Formato de cita no disponible.")

    response = HttpResponse(citation, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _escape_bibtex(value):
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(character, character) for character in value)