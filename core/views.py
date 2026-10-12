import mimetypes

from django.db.models import F
from django.db.models.functions import Coalesce
from django.http import FileResponse, Http404
from django.shortcuts import render

from blog.models import Post
from projects.models import Project
from research.models import ResearchItem
from .models import SiteProfile


def home(request):
    context = {
        "profile": SiteProfile.objects.first(),
        "recent_posts": (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .annotate(display_date=Coalesce("published_at", "created_at"))
            .order_by("-display_date", "-created_at")[:3]
        ),
        "highlighted_posts": Post.objects.filter(
            status=Post.Status.PUBLISHED,
            highlighted=True,
        )[:3],
        "recent_research": ResearchItem.objects.order_by(
            F("year").desc(nulls_last=True),
            "-created_at",
        )[:3],
        "recent_projects": Project.objects.order_by("-created_at")[:3],
    }
    return render(request, "core/home.html", context)


def portrait(request):
    return _profile_image_response("portrait", "No hay una imagen de perfil cargada.")


def home_image(request):
    return _profile_image_response(
        "home_image",
        "No hay una imagen de portada cargada.",
    )


def cv_photo(request):
    return _profile_image_response(
        "cv_photo",
        "No hay una foto para el currículum cargada.",
    )


def _profile_image_response(field_name, missing_message):
    profile = SiteProfile.objects.first()
    image = getattr(profile, field_name, None) if profile else None
    if not image:
        raise Http404(missing_message)

    content_type, _ = mimetypes.guess_type(image.name)
    return FileResponse(
        image.open("rb"),
        content_type=content_type or "application/octet-stream",
    )