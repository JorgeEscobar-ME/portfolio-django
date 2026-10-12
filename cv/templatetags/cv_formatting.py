from django import template
from django.utils.safestring import mark_safe

from cv.formatting import render_cv_markdown


register = template.Library()


@register.filter
def cv_markdown(value):
    if not value:
        return ""
    return mark_safe(render_cv_markdown(value))
