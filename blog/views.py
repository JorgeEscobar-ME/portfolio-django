from django.shortcuts import get_object_or_404, render

from django.db.models.functions import Coalesce

from .formatting import render_post_content
from .models import Post


def post_list(request):
    posts = (
        Post.objects.filter(status=Post.Status.PUBLISHED)
        .annotate(display_date=Coalesce("published_at", "created_at"))
        .order_by("-display_date", "-created_at")
    )
    selected_theme = request.GET.get("tema", "")
    theme_values = dict(Post.Theme.choices)
    if selected_theme in theme_values:
        posts = posts.filter(theme=selected_theme)
    else:
        selected_theme = ""

    return render(
        request,
        "blog/post_list.html",
        {
            "posts": posts,
            "themes": Post.Theme.choices,
            "selected_theme": selected_theme,
        },
    )


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)
    return render(
        request,
        "blog/post_detail.html",
        {"post": post, "rendered_content": render_post_content(post.content)},
    )