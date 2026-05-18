"""
report_generator.py — Generates a professional, personalised PDF audit report
Uses ReportLab only (no paid APIs). Design is clean, modern, and business-grade.
"""

import os
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.platypus import PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF

logger = logging.getLogger(__name__)

# ── Brand Palette ──────────────────────────────────────────────────────────────

BRAND_NAVY    = colors.HexColor("#0A1628")
BRAND_BLUE    = colors.HexColor("#1A56DB")
BRAND_ACCENT  = colors.HexColor("#00C2FF")
BRAND_LIGHT   = colors.HexColor("#EEF4FF")
BRAND_GRAY    = colors.HexColor("#64748B")
BRAND_TEXT    = colors.HexColor("#1E293B")
BRAND_WHITE   = colors.white
BRAND_GREEN   = colors.HexColor("#10B981")
BRAND_ORANGE  = colors.HexColor("#F59E0B")
BRAND_RED     = colors.HexColor("#EF4444")

W, H = A4  # 595.27 x 841.89 pts


# ── Style definitions ─────────────────────────────────────────────────────────

def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_company": ParagraphStyle(
            "cover_company",
            fontName="Helvetica-Bold",
            fontSize=28,
            textColor=BRAND_WHITE,
            leading=34,
            spaceAfter=8,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            fontName="Helvetica",
            fontSize=13,
            textColor=BRAND_ACCENT,
            leading=18,
            spaceAfter=4,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#94A3B8"),
            leading=14,
        ),
        "section_heading": ParagraphStyle(
            "section_heading",
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=BRAND_NAVY,
            leading=20,
            spaceBefore=18,
            spaceAfter=6,
        ),
        "sub_heading": ParagraphStyle(
            "sub_heading",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=BRAND_BLUE,
            leading=16,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10,
            textColor=BRAND_TEXT,
            leading=16,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
        ),
        "body_small": ParagraphStyle(
            "body_small",
            fontName="Helvetica",
            fontSize=9,
            textColor=BRAND_GRAY,
            leading=14,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=10,
            textColor=BRAND_TEXT,
            leading=16,
            leftIndent=16,
            spaceAfter=4,
        ),
        "highlight": ParagraphStyle(
            "highlight",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=BRAND_BLUE,
            leading=16,
            spaceAfter=6,
        ),
        "card_title": ParagraphStyle(
            "card_title",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=BRAND_GRAY,
            leading=12,
            spaceAfter=2,
        ),
        "card_value": ParagraphStyle(
            "card_value",
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=BRAND_NAVY,
            leading=20,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica",
            fontSize=8,
            textColor=BRAND_GRAY,
            leading=12,
            alignment=TA_CENTER,
        ),
    }
    return styles


# ── Cover Page ────────────────────────────────────────────────────────────────

def build_cover(story, lead, enriched, S):
    """Dark navy full-bleed cover with company name and report metadata."""

    # Background rectangle (simulated via a 1-row table with coloured cell)
    cover_data = [[""]]
    cover_tbl = Table(cover_data, colWidths=[W - 4*cm], rowHeights=[480])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_NAVY),
        ("ROUNDEDCORNERS", [12]),
        ("TOPPADDING",    (0, 0), (-1, -1), 50),
        ("LEFTPADDING",   (0, 0), (-1, -1), 40),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, -480))  # overlap content on top

    now   = datetime.utcnow()
    date  = now.strftime("%B %d, %Y")
    company = lead["company"]
    industry = enriched.get("industry") or "Technology"
    description = enriched.get("description", "")

    # Layered content using a table with transparent background
    cover_content = [
        [Paragraph("SimplifiIQ", ParagraphStyle("logo", fontName="Helvetica-Bold",
                   fontSize=11, textColor=BRAND_ACCENT, leading=16))],
        [Spacer(1, 30)],
        [Paragraph("BUSINESS AUDIT REPORT", ParagraphStyle("badge", fontName="Helvetica-Bold",
                   fontSize=9, textColor=colors.HexColor("#94A3B8"), leading=12,
                   spaceAfter=8))],
        [Paragraph(company, S["cover_company"])],
        [Paragraph(f"Industry: {industry}", S["cover_subtitle"])],
        [Spacer(1, 16)],
        [Paragraph(description[:200] + ("..." if len(description) > 200 else ""),
                   ParagraphStyle("cover_desc", fontName="Helvetica", fontSize=10,
                                  textColor=colors.HexColor("#CBD5E1"), leading=16))],
        [Spacer(1, 40)],
        [HRFlowable(width=200, thickness=1, color=BRAND_BLUE)],
        [Spacer(1, 12)],
        [Paragraph(f"Prepared for: <b>{lead['name']}</b>", S["cover_meta"])],
        [Paragraph(f"Date: {date}", S["cover_meta"])],
        [Paragraph(f"Prepared by: SimplifiIQ Research Engine", S["cover_meta"])],
    ]

    inner = Table([[row[0]] for row in cover_content], colWidths=[W - 8*cm])
    inner.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 40),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("TOPPADDING",   (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
    ]))
    story.append(inner)
    story.append(PageBreak())


# ── Section builders ──────────────────────────────────────────────────────────

def kpi_card(title: str, value: str, color=BRAND_BLUE) -> Table:
    """A small coloured metric card."""
    inner = Table(
        [[Paragraph(title.upper(), ParagraphStyle("ct", fontName="Helvetica-Bold",
                    fontSize=7, textColor=BRAND_WHITE, leading=10)),
          Paragraph(value, ParagraphStyle("cv", fontName="Helvetica-Bold",
                    fontSize=14, textColor=BRAND_WHITE, leading=18))]],
        colWidths=[None], rowHeights=[50]
    )
    inner.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), color),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [8]),
    ]))
    return inner


def info_row(label: str, value: str, S) -> list:
    return [
        Paragraph(f"<b>{label}</b>", S["body_small"]),
        Paragraph(value or "—", S["body"]),
    ]


def build_company_overview(story, lead, enriched, S):
    story.append(Paragraph("01. Company Overview", S["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=10))

    site_data = enriched.get("site_data", {})
    tagline   = site_data.get("tagline", "")
    desc      = enriched.get("description", "No description available.")
    website   = enriched.get("website") or lead.get("website") or "Not provided"
    industry  = enriched.get("industry") or lead.get("industry") or "General"

    info = [
        info_row("Company Name",  lead["company"], S),
        info_row("Industry",      industry,        S),
        info_row("Website",       website,         S),
        info_row("Contact Name",  lead["name"],    S),
        info_row("Contact Email", lead["email"],   S),
    ]
    if lead.get("team_size"):
        info.append(info_row("Team Size", lead["team_size"], S))

    tbl = Table(info, colWidths=[3.5*cm, 12*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (0, -1), BRAND_LIGHT),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("FONTNAME",     (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",    (0, 0), (0, -1), BRAND_NAVY),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 10))

    if tagline:
        story.append(Paragraph(f"<i>\"{tagline}\"</i>", ParagraphStyle("tagline_quote",
            fontName="Helvetica-Oblique", fontSize=11, textColor=BRAND_BLUE, leading=16,
            spaceAfter=8, leftIndent=20, borderPadding=(6, 0, 6, 12))))

    story.append(Paragraph(desc, S["body"]))

    # Paragraphs from website
    paras = site_data.get("paragraphs", [])
    if paras:
        story.append(Paragraph("From their website:", S["sub_heading"]))
        for p in paras[:2]:
            story.append(Paragraph(f"• {p}", S["bullet"]))


def build_digital_presence(story, lead, enriched, S):
    story.append(Paragraph("02. Digital Presence Analysis", S["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=10))

    social = enriched.get("social_links", {})
    linkedin_info = enriched.get("linkedin", {})
    website = enriched.get("website") or lead.get("website", "")

    has_website  = bool(website)
    has_linkedin = bool(social.get("linkedin") or linkedin_info.get("linkedin_url"))
    has_twitter  = bool(social.get("twitter"))
    has_facebook = bool(social.get("facebook"))

    # Score card
    score = sum([has_website, has_linkedin, has_twitter, has_facebook])
    score_pct = f"{score * 25}%"
    score_color = BRAND_GREEN if score >= 3 else (BRAND_ORANGE if score >= 2 else BRAND_RED)

    cards = Table([[
        kpi_card("DIGITAL SCORE",   score_pct,    score_color),
        kpi_card("WEBSITE",         "✓" if has_website  else "✗", BRAND_GREEN if has_website  else BRAND_RED),
        kpi_card("LINKEDIN",        "✓" if has_linkedin else "✗", BRAND_GREEN if has_linkedin else BRAND_RED),
        kpi_card("SOCIAL MEDIA",    "✓" if has_twitter or has_facebook else "✗",
                 BRAND_GREEN if (has_twitter or has_facebook) else BRAND_RED),
    ]], colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    cards.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    story.append(cards)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Findings:", S["sub_heading"]))
    findings = []
    if not has_website:
        findings.append("No verified company website found. This is a significant gap in digital credibility.")
    else:
        findings.append(f"Company website identified: {website}")
    if not has_linkedin:
        findings.append("No LinkedIn Company Page detected. LinkedIn is critical for B2B trust and talent.")
    else:
        findings.append(f"LinkedIn presence confirmed: {social.get('linkedin') or linkedin_info.get('linkedin_url')}")
    if not has_twitter:
        findings.append("No active Twitter/X presence found — a missed channel for brand awareness.")
    if not has_facebook:
        findings.append("Facebook presence not detected.")

    for f in findings:
        story.append(Paragraph(f"• {f}", S["bullet"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Recommendation: A unified digital presence strategy — encompassing SEO-optimised web content, "
        "regular LinkedIn publishing, and consistent social engagement — can dramatically improve "
        "inbound lead quality and brand authority in your sector.",
        S["body"]
    ))


def build_industry_insights(story, lead, enriched, S):
    story.append(Paragraph("03. Industry Intelligence & Trends", S["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=10))

    insights = enriched.get("industry_insights", {})
    industry = enriched.get("industry") or lead.get("industry") or "technology"

    story.append(Paragraph(
        f"The following intelligence has been compiled for the <b>{industry}</b> sector, "
        "highlighting where leading organisations are investing and where common operational "
        "inefficiencies exist.",
        S["body"]
    ))
    story.append(Spacer(1, 8))

    cards_data = [
        ("📈 Market Trend",    insights.get("trend", ""), BRAND_BLUE),
        ("⚠️ Common Pain Point", insights.get("pain", ""), BRAND_ORANGE),
        ("🚀 Key Opportunity", insights.get("opp", ""),  BRAND_GREEN),
    ]
    for label, text, color in cards_data:
        box = Table([[Paragraph(label, ParagraphStyle("il", fontName="Helvetica-Bold",
                    fontSize=9, textColor=color, leading=12)),
                     Paragraph(text, S["body"])]],
                    colWidths=[3.5*cm, 11*cm])
        box.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), BRAND_LIGHT),
            ("LEFTPADDING",  (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ("LINEABOVE",    (0, 0), (-1, 0), 2, color),
        ]))
        story.append(box)
        story.append(Spacer(1, 6))


def build_news_section(story, lead, enriched, S):
    headlines = enriched.get("news_headlines", [])
    if not headlines:
        return

    story.append(Paragraph("04. Recent News & Activity", S["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=10))
    story.append(Paragraph(
        f"The following recent headlines were found relating to {lead['company']}:",
        S["body"]
    ))
    for h in headlines:
        story.append(Paragraph(f"📰 {h}", S["bullet"]))
    story.append(Spacer(1, 6))


def build_automation_opportunities(story, lead, enriched, S):
    section_num = "05" if enriched.get("news_headlines") else "04"
    story.append(Paragraph(f"{section_num}. AI Automation Opportunities", S["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=10))

    company = lead["company"]
    industry = enriched.get("industry") or lead.get("industry") or "your industry"
    pain_points = lead.get("pain_points", "")

    story.append(Paragraph(
        f"Based on our research into {company} and sector benchmarks for {industry}, "
        "SimplifiIQ has identified the following high-impact automation opportunities:",
        S["body"]
    ))
    story.append(Spacer(1, 8))

    opportunities = [
        ("Lead Intake & Qualification",
         "Automate prospect research, scoring, and personalised first-response emails. "
         "Reduce lead response time from hours to seconds.",
         "HIGH"),
        ("Document Generation & Reporting",
         "Auto-generate client reports, proposals, and audit documents from structured data. "
         "Eliminate hours of manual formatting work.",
         "HIGH"),
        ("Data Enrichment Pipelines",
         "Continuously enrich your CRM with public data — company size, funding rounds, "
         "news triggers, social signals — without manual research.",
         "MEDIUM"),
        ("Customer Communication Automation",
         "Trigger contextual email sequences and follow-ups based on behaviour and CRM events. "
         "Improve response rates with AI personalisation.",
         "HIGH"),
        ("Internal Workflow Orchestration",
         "Connect your tools (CRM, calendar, email, project management) into automated "
         "pipelines that eliminate repetitive handoffs.",
         "MEDIUM"),
    ]

    if pain_points:
        opportunities.insert(0, (
            "Identified Pain Point",
            f"You mentioned: \"{pain_points[:200]}\". SimplifiIQ has targeted solutions addressing this specific challenge.",
            "CRITICAL"
        ))

    level_colors = {
        "CRITICAL": BRAND_RED,
        "HIGH":     BRAND_BLUE,
        "MEDIUM":   BRAND_ORANGE,
    }

    rows = [["Area", "Opportunity Description", "Priority"]]
    for area, desc, level in opportunities:
        rows.append([area, desc, level])

    col_widths = [3.5*cm, 10.5*cm, 1.8*cm]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl_style = [
        # Header
        ("BACKGROUND",   (0, 0), (-1, 0), BRAND_NAVY),
        ("TEXTCOLOR",    (0, 0), (-1, 0), BRAND_WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BRAND_WHITE, BRAND_LIGHT]),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]
    for i, (_, _, level) in enumerate(opportunities, start=1):
        color = level_colors.get(level, BRAND_GRAY)
        tbl_style.append(("TEXTCOLOR", (2, i), (2, i), color))
        tbl_style.append(("FONTNAME",  (2, i), (2, i), "Helvetica-Bold"))

    tbl.setStyle(TableStyle(tbl_style))
    story.append(tbl)


def build_recommendations(story, lead, enriched, S):
    story.append(Paragraph("06. Our Recommendations", S["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=10))

    company = lead["company"]
    recs = [
        ("Immediate", "Conduct an internal process audit to identify the top 3 workflows consuming the most manual effort. These are your highest-ROI automation targets."),
        ("Short-term (30 days)", f"Deploy a lead intake automation system similar to this report pipeline for {company}. Personalised first interactions significantly improve conversion rates."),
        ("Medium-term (90 days)", "Integrate an AI-powered data enrichment layer into your CRM to keep prospect and client profiles up-to-date automatically."),
        ("Strategic", "Develop an AI adoption roadmap aligned to your 12-month growth goals. SimplifiIQ can support this from strategy through to deployment."),
    ]

    for horizon, rec in recs:
        box_data = [[
            Paragraph(horizon, ParagraphStyle("rh", fontName="Helvetica-Bold", fontSize=9,
                                               textColor=BRAND_ACCENT, leading=12)),
            Paragraph(rec, S["body"])
        ]]
        box = Table(box_data, colWidths=[2.8*cm, 11.5*cm])
        box.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), BRAND_NAVY),
            ("TEXTCOLOR",    (1, 0), (1, 0), BRAND_WHITE),
            ("LEFTPADDING",  (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ]))
        story.append(box)
        story.append(Spacer(1, 6))


def build_next_steps(story, lead, S):
    story.append(Paragraph("07. Next Steps", S["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=10))

    story.append(Paragraph(
        f"Thank you for your interest, {lead['name']}. We'd love to explore how SimplifiIQ "
        f"can deliver measurable impact for {lead['company']}.",
        S["body"]
    ))
    story.append(Spacer(1, 8))

    steps = [
        ("1", "Reply to this report email to schedule a 30-minute discovery call."),
        ("2", "We'll conduct a deeper workflow audit specific to your operations."),
        ("3", "Receive a tailored automation blueprint with estimated ROI projections."),
        ("4", "Begin a pilot project with zero upfront commitment."),
    ]

    step_rows = [[
        Paragraph(num, ParagraphStyle("sn", fontName="Helvetica-Bold", fontSize=14,
                  textColor=BRAND_BLUE, leading=18, alignment=TA_CENTER)),
        Paragraph(text, S["body"])
    ] for num, text in steps]

    tbl = Table(step_rows, colWidths=[1.2*cm, 13.5*cm])
    tbl.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [BRAND_LIGHT, BRAND_WHITE]),
    ]))
    story.append(tbl)

    story.append(Spacer(1, 20))
    contact_box = Table([[
        Paragraph(
            "📧 career@simplifiiq.com &nbsp;&nbsp;|&nbsp;&nbsp; 🌐 simplifiiq.com",
            ParagraphStyle("contact", fontName="Helvetica-Bold", fontSize=11,
                           textColor=BRAND_WHITE, leading=16, alignment=TA_CENTER)
        )
    ]], colWidths=[W - 4*cm])
    contact_box.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), BRAND_BLUE),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
    ]))
    story.append(contact_box)


# ── Page template callbacks ───────────────────────────────────────────────────

def on_page(canvas, doc, company: str):
    """Draw header and footer on every page (except cover)."""
    canvas.saveState()
    page = doc.page

    if page > 1:
        # Top strip
        canvas.setFillColor(BRAND_NAVY)
        canvas.rect(0, H - 1.2*cm, W, 1.2*cm, fill=1, stroke=0)
        canvas.setFillColor(BRAND_WHITE)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(1.5*cm, H - 0.85*cm, "SimplifiIQ")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        canvas.drawRightString(W - 1.5*cm, H - 0.85*cm, f"{company} — Business Audit Report")

        # Bottom strip
        canvas.setFillColor(BRAND_LIGHT)
        canvas.rect(0, 0, W, 1*cm, fill=1, stroke=0)
        canvas.setFillColor(BRAND_GRAY)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(1.5*cm, 0.38*cm,
                          "Confidential | Generated by SimplifiIQ Research Engine | simplifiiq.com")
        canvas.drawRightString(W - 1.5*cm, 0.38*cm, f"Page {page}")

    canvas.restoreState()


# ── Main entry ────────────────────────────────────────────────────────────────

def generate_pdf_report(lead: dict, enriched: dict, output_path: str):
    """Generate the full multi-section PDF report."""
    company = lead["company"]

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=1.8*cm,
        title=f"{company} — Business Audit Report",
        author="SimplifiIQ",
        subject="AI Automation Opportunity Assessment",
    )

    S = build_styles()
    story = []

    # Cover
    build_cover(story, lead, enriched, S)

    # Sections
    build_company_overview(story, lead, enriched, S)
    story.append(Spacer(1, 10))

    build_digital_presence(story, lead, enriched, S)
    story.append(Spacer(1, 10))

    build_industry_insights(story, lead, enriched, S)
    story.append(Spacer(1, 10))

    build_news_section(story, lead, enriched, S)

    build_automation_opportunities(story, lead, enriched, S)
    story.append(Spacer(1, 10))

    build_recommendations(story, lead, enriched, S)
    story.append(Spacer(1, 10))

    build_next_steps(story, lead, S)

    # Build
    doc.build(
        story,
        onFirstPage=lambda c, d: on_page(c, d, company),
        onLaterPages=lambda c, d: on_page(c, d, company),
    )
    logger.info(f"📄 PDF saved: {output_path}")
