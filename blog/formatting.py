import html
import re
import uuid

import bleach
import markdown


_MATH_PATTERN = re.compile(
    r"\$\$(?P<display>.*?)\$\$|(?<!\$)\$(?!\$)(?P<inline>[^$\n]+?)(?<!\$)\$(?!\$)",
    re.DOTALL,
)
_ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "del",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "span",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}


def render_post_content(content):
    nonce = uuid.uuid4().hex
    math_expressions = {}

    def preserve_math(match):
        token = f"MATH{nonce}{len(math_expressions)}TOKEN"
        display_expression = match.group("display")
        if display_expression is not None:
            math_expressions[token] = (
                f'<span class="math-display">\\[{html.escape(display_expression)}\\]</span>'
            )
        else:
            math_expressions[token] = (
                f'<span class="math-inline">\\({html.escape(match.group("inline"))}\\)</span>'
            )
        return token

    source = _MATH_PATTERN.sub(preserve_math, content)
    rendered = markdown.markdown(
        source,
        extensions=["fenced_code", "nl2br", "sane_lists", "tables"],
    )
    for token, expression in math_expressions.items():
        rendered = rendered.replace(token, expression)

    return bleach.clean(
        rendered,
        tags=_ALLOWED_TAGS,
        attributes={
            "a": ["href", "title"],
            "code": ["class"],
            "img": ["src", "alt", "title"],
            "pre": ["class"],
            "span": ["class"],
        },
        protocols=["http", "https", "mailto"],
        strip=True,
    )
