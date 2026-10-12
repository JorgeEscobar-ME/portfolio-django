from html import escape
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from core.models import SiteProfile

from .models import CVProfile, Certification, Education, Experience, ResearchProduct, Skill
from .formatting import markdown_to_reportlab_flowables


def cv_detail(request):
    context = _cv_context()
    return render(request, "cv/cv_detail.html", context)


def cv_pdf(request):
    context = _cv_context()
    profile = context["profile"]
    buffer = BytesIO()
    styles = _pdf_styles()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=24 * mm,
        bottomMargin=20 * mm,
        title=f"Currículum — {profile.name if profile else 'Portafolio'}",
        author=profile.name if profile else "Portafolio",
    )
    story = []

    if profile:
        identity = [Paragraph(_pdf_text(profile.name), styles["CVName"])]
        if profile.headline:
            identity.append(Paragraph(_pdf_text(profile.headline), styles["CVHeadline"]))
        contacts = [
            profile.public_email,
            profile.linkedin_url,
            profile.github_url,
        ]
        contact_line = "  ·  ".join(escape(value) for value in contacts if value)
        if contact_line:
            identity.append(Paragraph(contact_line, styles["CVContact"]))
        if profile.cv_photo:
            with profile.cv_photo.open("rb") as photo_file:
                photo_data = photo_file.read()
            photo = Image(BytesIO(photo_data), width=32 * mm, height=40 * mm)
            identity_table = Table(
                [[photo, identity]],
                colWidths=[38 * mm, 134 * mm],
                hAlign="LEFT",
            )
            identity_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (0, 0), 6 * mm),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            story.append(identity_table)
        else:
            story.extend(identity)
        cv_profile = context["cv_profile"]
        summary = (
            cv_profile.summary
            if cv_profile and cv_profile.summary
            else profile.biography
        )
        if summary:
            story.extend(
                [
                    Spacer(1, 3 * mm),
                ]
            )
            story.extend(markdown_to_reportlab_flowables(summary, styles))
        story.append(Spacer(1, 4 * mm))

    _append_experience(
        story,
        styles,
        context["experiences"],
        "Experiencia profesional",
    )
    _append_experience(
        story,
        styles,
        context["teaching_experiences"],
        "Experiencia docente",
    )
    _append_education(story, styles, context["education"])
    _append_research_products(story, styles, context["research_products"])
    _append_skills(story, styles, context["skills"])
    _append_certifications(story, styles, context["certifications"])

    if not story:
        story.append(
            Paragraph(
                "Agrega tu perfil y experiencia desde el panel de administración.",
                styles["CVBody"],
            )
        )

    document.build(story, onFirstPage=_draw_pdf_chrome, onLaterPages=_draw_pdf_chrome)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    filename = slugify(profile.name) if profile else "curriculum"
    response["Content-Disposition"] = f'attachment; filename="{filename}-cv.pdf"'
    return response


def _cv_context():
    return {
        "profile": SiteProfile.objects.first(),
        "cv_profile": CVProfile.objects.first(),
        "experiences": Experience.objects.filter(type=Experience.Type.PROFESSIONAL),
        "teaching_experiences": Experience.objects.filter(type=Experience.Type.TEACHING),
        "education": Education.objects.all(),
        "skills": Skill.objects.all(),
        "certifications": Certification.objects.all(),
        "research_products": ResearchProduct.objects.all(),
    }


def _pdf_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "CVName",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=29,
            textColor=colors.HexColor("#24170D"),
            alignment=TA_LEFT,
            spaceAfter=3 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            "CVHeadline",
            parent=styles["Normal"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#A75F2C"),
            spaceAfter=2 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            "CVContact",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#654D3A"),
            splitLongWords=True,
        )
    )
    styles.add(
        ParagraphStyle(
            "CVSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#A75F2C"),
            spaceBefore=5 * mm,
            spaceAfter=2 * mm,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            "CVEntry",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#24170D"),
            spaceBefore=2 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            "CVMeta",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#765C46"),
        )
    )
    styles.add(
        ParagraphStyle(
            "CVBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#47382D"),
            spaceAfter=1.5 * mm,
        )
    )
    return styles


def _pdf_text(value):
    return escape(value).replace("\n", "<br/>")


def _append_section_title(story, title, styles):
    story.extend(
        [
            Paragraph(escape(title), styles["CVSection"]),
            HRFlowable(
                width="100%",
                thickness=0.8,
                color=colors.HexColor("#EDBA84"),
                spaceAfter=2 * mm,
            ),
        ]
    )


def _format_period(start_date, end_date, current):
    start = start_date.strftime("%m/%Y") if start_date else ""
    end = "Actualidad" if current else end_date.strftime("%m/%Y") if end_date else ""
    return " – ".join(part for part in (start, end) if part)


def _append_experience(story, styles, experiences, heading):
    if not experiences:
        return
    _append_section_title(story, heading, styles)
    for item in experiences:
        period = _format_period(item.start_date, item.end_date, item.current)
        meta = " · ".join(
            part
            for part in (
                item.organization,
                item.location,
                item.get_dedication_display() if item.dedication else "",
                period,
            )
            if part
        )
        entry = [
            Paragraph(_pdf_text(item.role), styles["CVEntry"]),
            Paragraph(_pdf_text(meta), styles["CVMeta"]),
        ]
        if item.description:
            entry.extend(markdown_to_reportlab_flowables(item.description, styles))
        story.append(KeepTogether(entry))


def _append_research_products(story, styles, products):
    if not products:
        return
    _append_section_title(story, "Productos de investigación", styles)
    for item in products:
        meta = " · ".join(
            part
            for part in (
                item.get_product_type_display(),
                item.venue,
                str(item.year) if item.year else "",
                item.identifier,
                item.authors,
            )
            if part
        )
        entry = [
            Paragraph(_pdf_text(item.title), styles["CVEntry"]),
            Paragraph(_pdf_text(meta), styles["CVMeta"]),
        ]
        if item.description:
            entry.extend(markdown_to_reportlab_flowables(item.description, styles))
        if item.product_url:
            entry.append(Paragraph(_pdf_text(item.product_url), styles["CVMeta"]))
        story.append(KeepTogether(entry))


def _append_education(story, styles, education):
    if not education:
        return
    _append_section_title(story, "Formación académica", styles)
    for item in education:
        period = _format_period(item.start_date, item.end_date, item.current)
        meta = " · ".join(part for part in (item.institution, item.location, period) if part)
        entry = [
            Paragraph(_pdf_text(item.degree), styles["CVEntry"]),
            Paragraph(_pdf_text(meta), styles["CVMeta"]),
        ]
        if item.details:
            entry.extend(markdown_to_reportlab_flowables(item.details, styles))
        story.append(KeepTogether(entry))


def _append_skills(story, styles, skills):
    if not skills:
        return
    _append_section_title(story, "Habilidades", styles)
    for category, label in Skill.Category.choices:
        items = [skill for skill in skills if skill.category == category]
        if not items:
            continue
        value = ", ".join(
            f"{escape(item.name)}"
            + (f" ({escape(item.proficiency)})" if item.proficiency else "")
            for item in items
        )
        story.append(
            Paragraph(f"<b>{escape(label)}:</b> {value}", styles["CVBody"])
        )


def _append_certifications(story, styles, certifications):
    if not certifications:
        return
    _append_section_title(story, "Certificaciones", styles)
    for item in certifications:
        parts = [item.issuer]
        if item.issued_on:
            parts.append(item.issued_on.strftime("%m/%Y"))
        if item.credential_url:
            parts.append(item.credential_url)
        story.append(
            KeepTogether(
                [
                    Paragraph(_pdf_text(item.title), styles["CVEntry"]),
                    Paragraph(_pdf_text(" · ".join(parts)), styles["CVMeta"]),
                ]
            )
        )


def _draw_pdf_chrome(canvas, document):
    canvas.saveState()
    page_width, page_height = A4
    canvas.setFillColor(colors.HexColor("#EDBA84"))
    canvas.rect(0, page_height - 7 * mm, page_width, 7 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#E7D8C8"))
    canvas.setLineWidth(0.5)
    canvas.line(19 * mm, 14 * mm, page_width - 19 * mm, 14 * mm)
    canvas.setFillColor(colors.HexColor("#765C46"))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(page_width - 19 * mm, 9 * mm, str(document.page))
    canvas.restoreState()
