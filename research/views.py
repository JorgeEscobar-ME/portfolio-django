from django.shortcuts import get_object_or_404, render

from .models import ResearchItem


def research_list(request):
    items = ResearchItem.objects.all()
    return render(request, "research/research_list.html", {"items": items})


def research_detail(request, slug):
    item = get_object_or_404(ResearchItem, slug=slug)
    return render(request, "research/research_detail.html", {"item": item})