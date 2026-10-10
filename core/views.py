from django.shortcuts import render

from blog.models import Post
from projects.models import Project
from research.models import ResearchItem
from .models import SiteProfile


def home(request):
    context = {
        "profile": SiteProfile.objects.first(),
        "recent_posts": Post.objects.filter(status=Post.Status.PUBLISHED)[:3],
        "recent_research": ResearchItem.objects.all()[:3],
        "featured_projects": Project.objects.filter(featured=True)[:3],
    }
    return render(request, "core/home.html", context)