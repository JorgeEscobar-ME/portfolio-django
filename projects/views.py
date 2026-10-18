import mimetypes

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render

from blog.formatting import render_post_content

from .models import Project


def project_list(request):
    projects = Project.objects.filter(status=Project.Status.PUBLISHED)
    return render(request, "projects/project_list.html", {"projects": projects})


def project_detail(request, slug):
    project = get_object_or_404(
        Project,
        slug=slug,
        status=Project.Status.PUBLISHED,
    )
    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "rendered_article_content": (
                render_post_content(project.article_content)
                if project.article_content
                else ""
            ),
        },
    )


def project_cover(request, slug):
    project = get_object_or_404(
        Project,
        slug=slug,
        status=Project.Status.PUBLISHED,
    )
    if not project.cover_image:
        raise Http404("Este proyecto no tiene una imagen de portada.")

    content_type, _ = mimetypes.guess_type(project.cover_image.name)
    return FileResponse(
        project.cover_image.open("rb"),
        content_type=content_type or "application/octet-stream",
    )