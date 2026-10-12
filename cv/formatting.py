from html import escape
from html.parser import HTMLParser

import bleach
import markdown
from reportlab.lib import colors
from reportlab.platypus import ListFlowable, ListItem, Paragraph


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
    "li",
    "ol",
    "p",
    "strong",
    "ul",
}
_BLOCK_TAGS = {"blockquote", "h1", "h2", "h3", "h4", "h5", "h6", "p"}
_VOID_TAGS = {"br", "hr"}
_REPORTLAB_TAGS = {
    "strong": "b",
    "em": "i",
    "del": "strike",
}


def render_cv_markdown(source):
    rendered = markdown.markdown(
        source,
        extensions=["nl2br", "sane_lists"],
    )
    return bleach.clean(
        rendered,
        tags=_ALLOWED_TAGS,
        attributes={"a": ["href", "title"]},
        protocols=["http", "https", "mailto"],
        strip=True,
    )


def markdown_to_reportlab_flowables(source, styles):
    parser = _CVHTMLParser()
    parser.feed(render_cv_markdown(source))
    return _block_flowables(parser.root, styles)


class _HTMLNode:
    def __init__(self, tag=None, attributes=None):
        self.tag = tag
        self.attributes = dict(attributes or ())
        self.children = []


class _CVHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _HTMLNode()
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _HTMLNode(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in _VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(_HTMLNode(tag, attrs))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _inline_markup(node):
    if isinstance(node, str):
        return escape(node)
    if node.tag == "br":
        return "<br/>"
    content = "".join(_inline_markup(child) for child in node.children)
    tag = _REPORTLAB_TAGS.get(node.tag, node.tag)
    if tag == "code":
        return f'<font name="Courier">{content}</font>'
    if tag == "a":
        href = escape(node.attributes.get("href", ""), quote=True)
        return f'<link href="{href}">{content}</link>' if href else content
    if tag == "span":
        return content
    return f"<{tag}>{content}</{tag}>" if tag in {"b", "i", "strike"} else content


def _paragraph_from_nodes(nodes, styles, bold=False):
    content = "".join(_inline_markup(node) for node in nodes).strip()
    if not content:
        return None
    if bold:
        content = f"<b>{content}</b>"
    return Paragraph(content, styles["CVBody"])


def _block_flowables(container, styles):
    flowables = []
    inline_nodes = []

    def flush_inline():
        paragraph = _paragraph_from_nodes(inline_nodes, styles)
        if paragraph:
            flowables.append(paragraph)
        inline_nodes.clear()

    for node in container.children:
        if isinstance(node, str):
            if node.strip():
                inline_nodes.append(node)
            continue
        if node.tag in {"ul", "ol"}:
            flush_inline()
            items = [
                ListItem(_block_flowables(item, styles), leftIndent=0)
                for item in node.children
                if isinstance(item, _HTMLNode) and item.tag == "li"
            ]
            if items:
                flowables.append(
                    ListFlowable(
                        items,
                        bulletType="bullet" if node.tag == "ul" else "1",
                        leftIndent=14,
                        bulletFontName="Helvetica",
                        bulletFontSize=8,
                        bulletColor=colors.HexColor("#765C46"),
                        spaceAfter=2,
                    )
                )
        elif node.tag in _BLOCK_TAGS:
            flush_inline()
            if node.tag == "blockquote":
                flowables.extend(_block_flowables(node, styles))
            else:
                paragraph = _paragraph_from_nodes(
                    node.children,
                    styles,
                    bold=node.tag.startswith("h"),
                )
                if paragraph:
                    flowables.append(paragraph)
        elif node.tag == "hr":
            flush_inline()
        else:
            inline_nodes.append(node)
    flush_inline()
    return flowables
