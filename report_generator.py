"""
report_generator.py — Professional PDF audit report generator
Uses ReportLab only. Clean, modern, business-grade design with proper table alignment.
Author: Kalyan Dakkili
"""

import os
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)

logger = logging.getLogger(__name__)

# ── Brand Colors ───────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#0A1628")
BLUE    = colors.HexColor("#1A56DB")
ACCENT  = colors.HexColor("#00C2FF")
LIGHT   = colors.HexColor("#EEF4FF")
GRAY    = colors.HexColor("#64748B")
TEXT    = colors.HexColor("#1E293B")
WHITE   = colors.white
GREEN   = colors.HexColor("#10B981")
ORANGE  = colors.HexColor("#F59E0B")
RED     = colors.HexColor("#EF4444")
SILVER  = colors.HexColor("#F8FAFC")

W, H = A4


# ── Styles ─────────────────────────────────────────────────────────────────────
def styles():
    return {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22,
                             textColor=WHITE, leading=28, spaceAfter=6),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14,
                             textColor=NAVY, leading=20, spaceBefore=14, spaceAfter=6),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11,
                             textColor=BLUE, leading=16, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.5,
                               textColor=TEXT, leading=15, spaceAfter=5,
                               alignment=TA_JUSTIFY),
        "body_white": ParagraphStyle("body_white", fontName="Helvetica", fontSize=9.5,
                                     textColor=WHITE, leading=15, spaceAfter=5,
                                     alignment=TA_JUSTIFY),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8.5,
                                textColor=GRAY, leading=13, spaceAfter=3),
        "small_bold": ParagraphStyle("small_bold", fontName="Helvetica-Bold", fontSize=8.5,
                                     textColor=NAVY, leading=13, spaceAfter=3),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.5,
                                 textColor=TEXT, leading=15, leftIndent=12, spaceAfter=4),
        "cover_tag": ParagraphStyle("cover_tag", fontName="Helvetica-Bold", fontSize=8,
                                    textColor=ACCENT, leading=12, spaceAfter=8,
                                    letterSpacing=1.5),
        "cover_company": ParagraphStyle("cover_company", fontName="Helvetica-Bold",
                                        fontSize=30, textColor=WHITE, leading=36, spaceAfter=6),
        "cover_sub": ParagraphStyle("cover_sub", fontName="Helvetica", fontSize=12,
                                    textColor=ACCENT, leading=18, spaceAfter=4),
        "cover_meta": ParagraphStyle("cover_meta", fontName="Helvetica", fontSize=9,
                                     textColor=colors.HexColor("#94A3B8"), leading=14),
        "tag_white": ParagraphStyle("tag_white", fontName="Helvetica-Bold", fontSize=8,
                                    textColor=WHITE, leading=12),
        "center": ParagraphStyle("center", fontName="Helvetica", fontSize=9.5,
                                 textColor=TEXT, leading=15, alignment=TA_CENTER),
        "center_white": ParagraphStyle("center_white", fontName="Helvetica-Bold", fontSize=11,
                                       textColor=WHITE, leading=16, alignment=TA_CENTER),
        "number": ParagraphStyle("number", fontName="Helvetica-Bold", fontSize=16,
                                 textColor=BLUE, leading=20, alignment=TA_CENTER),
        "priority_high": ParagraphStyle("ph", fontName="Helvetica-Bold", fontSize=8,
                                        textColor=BLUE, leading=12, alignment=TA_CENTER),
        "priority_medium": ParagraphStyle("pm", fontName="Helvetica-Bold", fontSize=8,
                                          textColor=ORANGE, leading=12, alignment=TA_CENTER),
        "priority_critical": ParagraphStyle("pc", fontName="Helvetica-Bold", fontSize=8,
                                            textColor=RED, leading=12, alignment=TA_CENTER),
        "table_header": ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9,
                                       textColor=WHITE, leading=13),
        "table_cell": ParagraphStyle("tc", fontName="Helvetica", fontSize=9,
                                     textColor=TEXT, leading=14),
        "table_cell_bold": ParagraphStyle("tcb", fontName="Helvetica-Bold", fontSize=9,
                                          textColor=NAVY, leading=14),
    }


# ── Cover Page ─────────────────────────────────────────────────────────────────
def build_cover(story, lead, enriched, S):
    company  = lead["company"]
    industry = enriched.get("industry") or lead.get("industry") or "Technology"
    desc     = enriched.get("description", "")
    date     = datetime.utcnow().strftime("%B %d, %Y")

    # Full-width dark cover block
    cover_rows = [
        [Paragraph("SimplifiIQ", ParagraphStyle("logo", fontName="Helvetica-Bold",
                   fontSize=12, textColor=ACCENT, leading=16))],
        [Spacer(1, 24)],
        [Paragraph("BUSINESS AUDIT REPORT", S["cover_tag"])],
        [Paragraph(company, S["cover_company"])],
        [Paragraph(f"Industry: {industry}", S["cover_sub"])],
        [Spacer(1, 12)],
        [Paragraph(
            desc[:220] + ("..." if len(desc) > 220 else "") if desc else
            f"{company} operates in the {industry} sector. This report provides an "
            "AI-powered analysis of their digital presence, industry positioning, and "
            "automation opportunities.",
            ParagraphStyle("cover_desc", fontName="Helvetica", fontSize=10,
                           textColor=colors.HexColor("#CBD5E1"), leading=16)
        )],
        [Spacer(1, 36)],
        [HRFlowable(width=180, thickness=1, color=BLUE)],
        [Spacer(1, 12)],
        [Paragraph(f"<b>Prepared for:</b> {lead['name']}", S["cover_meta"])],
        [Paragraph(f"<b>Date:</b> {date}", S["cover_meta"])],
        [Paragraph("<b>Prepared by:</b> SimplifiIQ Research Engine", S["cover_meta"])],
        [Spacer(1, 8)],
    ]

    cover_tbl = Table(cover_rows, colWidths=[W - 4*cm])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 42),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 30),
    ]))
    story.append(cover_tbl)
    story.append(PageBreak())


# ── Section Header ──────────────────────────────────────────────────────────────
def section_header(story, number, title, S):
    header = Table(
        [[Paragraph(number, ParagraphStyle("sn", fontName="Helvetica-Bold", fontSize=9,
                   textColor=ACCENT, leading=12)),
          Paragraph(title, ParagraphStyle("st", fontName="Helvetica-Bold", fontSize=14,
                   textColor=WHITE, leading=20))]],
        colWidths=[1.2*cm, W - 4*cm - 1.2*cm]
    )
    header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header)
    story.append(Spacer(1, 10))


# ── 01. Company Overview ────────────────────────────────────────────────────────
def build_company_overview(story, lead, enriched, S):
    section_header(story, "01", "Company Overview", S)

    site_data = enriched.get("site_data", {})
    tagline   = site_data.get("tagline", "")
    desc      = enriched.get("description", "No description available.")
    website   = enriched.get("website") or lead.get("website") or "Not provided"
    industry  = enriched.get("industry") or lead.get("industry") or "General"

    # Info table — 2 columns, clean grid
    rows = [
        [Paragraph("Company Name",  S["small_bold"]), Paragraph(lead["company"], S["body"])],
        [Paragraph("Industry",      S["small_bold"]), Paragraph(industry,         S["body"])],
        [Paragraph("Website",       S["small_bold"]), Paragraph(website,           S["body"])],
        [Paragraph("Contact Name",  S["small_bold"]), Paragraph(lead["name"],      S["body"])],
        [Paragraph("Contact Email", S["small_bold"]), Paragraph(lead["email"],     S["body"])],
    ]
    if lead.get("team_size"):
        rows.append([Paragraph("Team Size", S["small_bold"]),
                     Paragraph(lead["team_size"], S["body"])])

    tbl = Table(rows, colWidths=[4*cm, W - 4*cm - 4*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), LIGHT),
        ("BACKGROUND",    (1, 0), (1, -1), WHITE),
        ("ROWBACKGROUNDS",(1, 0), (1, -1), [WHITE, SILVER]),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 10))

    if tagline:
        quote = Table([[Paragraph(f'"{tagline}"',
                        ParagraphStyle("q", fontName="Helvetica-Oblique", fontSize=11,
                                       textColor=BLUE, leading=16))]],
                      colWidths=[W - 4*cm])
        quote.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), LIGHT),
            ("LEFTPADDING",  (0, 0), (-1, -1), 16),
            ("RIGHTPADDING", (0, 0), (-1, -1), 16),
            ("TOPPADDING",   (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
            ("LINERIGHT",    (0, 0), (0, -1), 3, BLUE),
        ]))
        story.append(quote)
        story.append(Spacer(1, 8))

    story.append(Paragraph(desc, S["body"]))

    paras = site_data.get("paragraphs", [])
    if paras:
        story.append(Paragraph("From their website:", S["h3"]))
        for p in paras[:2]:
            story.append(Paragraph(f"• {p}", S["bullet"]))

    story.append(Spacer(1, 16))


# ── 02. Digital Presence ────────────────────────────────────────────────────────
def build_digital_presence(story, lead, enriched, S):
    section_header(story, "02", "Digital Presence Analysis", S)

    social       = enriched.get("social_links", {})
    linkedin_info= enriched.get("linkedin", {})
    website      = enriched.get("website") or lead.get("website", "")

    has_website  = bool(website)
    has_linkedin = bool(social.get("linkedin") or linkedin_info.get("linkedin_url"))
    has_twitter  = bool(social.get("twitter"))
    has_facebook = bool(social.get("facebook"))
    score        = sum([has_website, has_linkedin, has_twitter, has_facebook])
    score_pct    = f"{score * 25}%"
    score_color  = GREEN if score >= 3 else (ORANGE if score >= 2 else RED)

    def metric_cell(label, val, val_color):
        return Table([[
            Paragraph(label, ParagraphStyle("ml", fontName="Helvetica-Bold", fontSize=7,
                      textColor=colors.HexColor("#94A3B8"), leading=10)),
            Paragraph(val, ParagraphStyle("mv", fontName="Helvetica-Bold", fontSize=18,
                      textColor=WHITE, leading=22, alignment=TA_CENTER)),
        ]], colWidths=[None], rowHeights=[52])

    def score_card(label, val, color):
        t = Table([[Paragraph(label, ParagraphStyle("sl", fontName="Helvetica-Bold",
                   fontSize=7.5, textColor=colors.HexColor("#CBD5E1"), leading=10)),
                   Paragraph(val, ParagraphStyle("sv", fontName="Helvetica-Bold",
                   fontSize=20, textColor=WHITE, leading=24))]],
                  colWidths=[None], rowHeights=[56])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), color),
            ("LEFTPADDING",   (0, 0), (-1, -1), 14),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        return t

    cards = Table([[
        score_card("DIGITAL SCORE", score_pct, score_color),
        score_card("WEBSITE",  "✓" if has_website  else "✗", GREEN if has_website  else RED),
        score_card("LINKEDIN", "✓" if has_linkedin else "✗", GREEN if has_linkedin else RED),
        score_card("SOCIAL",   "✓" if (has_twitter or has_facebook) else "✗",
                   GREEN if (has_twitter or has_facebook) else RED),
    ]], colWidths=[(W - 4*cm)/4]*4)
    cards.setStyle(TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(cards)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Key Findings:", S["h3"]))
    findings = []
    if has_website:
        findings.append(f"✓ Company website identified: {website}")
    else:
        findings.append("✗ No verified company website found — a significant gap in digital credibility.")
    if has_linkedin:
        findings.append(f"✓ LinkedIn presence confirmed.")
    else:
        findings.append("✗ No LinkedIn Company Page detected — critical for B2B trust and talent acquisition.")
    if not has_twitter:
        findings.append("✗ No active Twitter/X presence — a missed channel for brand awareness.")
    if not has_facebook:
        findings.append("✗ Facebook presence not detected.")

    for f in findings:
        color = TEXT if "✓" in f else colors.HexColor("#DC2626")
        story.append(Paragraph(f"  {f}", ParagraphStyle("fi", fontName="Helvetica",
                     fontSize=9.5, textColor=color, leading=15, spaceAfter=4)))

    story.append(Spacer(1, 8))
    rec = Table([[Paragraph(
        "💡 Recommendation: A unified digital presence strategy — SEO-optimised web content, "
        "regular LinkedIn publishing, and consistent social engagement — can dramatically improve "
        "inbound lead quality and brand authority in your sector.",
        S["body"])]],
        colWidths=[W - 4*cm])
    rec.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINERIGHT",     (0, 0), (0, -1), 3, ACCENT),
    ]))
    story.append(rec)
    story.append(Spacer(1, 16))


# ── 03. Industry Intelligence ───────────────────────────────────────────────────
def build_industry_insights(story, lead, enriched, S):
    section_header(story, "03", "Industry Intelligence & Trends", S)

    insights = enriched.get("industry_insights", {})
    industry = enriched.get("industry") or lead.get("industry") or "Technology"

    story.append(Paragraph(
        f"The following intelligence has been compiled for the <b>{industry}</b> sector, "
        "highlighting where leading organisations are investing and where common operational "
        "inefficiencies exist.",
        S["body"]
    ))
    story.append(Spacer(1, 10))

    cards = [
        ("📈 Market Trend",       insights.get("trend", ""), BLUE),
        ("⚠️  Common Pain Point", insights.get("pain", ""), ORANGE),
        ("🚀 Key Opportunity",    insights.get("opp",  ""), GREEN),
    ]

    for label, text, color in cards:
        row = Table([[
            Paragraph(label, ParagraphStyle("il", fontName="Helvetica-Bold", fontSize=9,
                      textColor=color, leading=13)),
            Paragraph(text, S["body"])
        ]], colWidths=[4*cm, W - 4*cm - 4*cm])
        row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), LIGHT),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LINEABOVE",     (0, 0), (-1, 0), 2.5, color),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(row)
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 10))


# ── 04. Recent News ─────────────────────────────────────────────────────────────
def build_news_section(story, lead, enriched, S):
    headlines = enriched.get("news_headlines", [])
    if not headlines:
        return

    section_header(story, "04", "Recent News & Activity", S)
    story.append(Paragraph(
        f"The following recent headlines were identified relating to {lead['company']}:",
        S["body"]
    ))
    story.append(Spacer(1, 6))
    for h in headlines:
        story.append(Paragraph(f"📰  {h}", S["bullet"]))
    story.append(Spacer(1, 16))


# ── 05. AI Automation Opportunities ────────────────────────────────────────────
def build_automation_opportunities(story, lead, enriched, S):
    num = "05" if enriched.get("news_headlines") else "04"
    section_header(story, num, "AI Automation Opportunities", S)

    company    = lead["company"]
    industry   = enriched.get("industry") or lead.get("industry") or "your industry"
    pain_points= lead.get("pain_points", "")

    story.append(Paragraph(
        f"Based on our research into <b>{company}</b> and sector benchmarks for <b>{industry}</b>, "
        "SimplifiIQ has identified the following high-impact automation opportunities:",
        S["body"]
    ))
    story.append(Spacer(1, 10))

    opportunities = [
        ("Lead Intake & Qualification",
         "Automate prospect research, scoring, and personalised first-response emails. "
         "Reduce lead response time from hours to seconds.",
         "HIGH", BLUE),
        ("Document Generation",
         "Auto-generate client reports, proposals, and audit documents from structured data. "
         "Eliminate hours of manual formatting work per week.",
         "HIGH", BLUE),
        ("Data Enrichment Pipelines",
         "Continuously enrich your CRM with public data — company size, funding rounds, "
         "news triggers, and social signals — without manual research.",
         "MEDIUM", ORANGE),
        ("Customer Communication",
         "Trigger contextual email sequences and follow-ups based on behaviour and CRM events. "
         "Improve response rates significantly with AI personalisation.",
         "HIGH", BLUE),
        ("Internal Workflow Orchestration",
         "Connect your tools (CRM, calendar, email, project management) into automated "
         "pipelines that eliminate repetitive handoffs between teams.",
         "MEDIUM", ORANGE),
    ]

    if pain_points:
        opportunities.insert(0, (
            "Your Identified Pain Point",
            f"You mentioned: \"{pain_points[:180]}\". SimplifiIQ has targeted solutions addressing this specific challenge.",
            "CRITICAL", RED
        ))

    # Header row
    header = Table([[
        Paragraph("AREA", S["table_header"]),
        Paragraph("OPPORTUNITY DESCRIPTION", S["table_header"]),
        Paragraph("PRIORITY", S["table_header"]),
    ]], colWidths=[4.5*cm, 10*cm, 2*cm])
    header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(header)

    # Data rows
    for i, (area, desc, level, color) in enumerate(opportunities):
        bg = WHITE if i % 2 == 0 else SILVER
        row = Table([[
            Paragraph(area, S["table_cell_bold"]),
            Paragraph(desc, S["table_cell"]),
            Paragraph(level, ParagraphStyle("pr", fontName="Helvetica-Bold", fontSize=7.5,
                      textColor=color, leading=11, alignment=TA_CENTER)),
        ]], colWidths=[4.5*cm, 10*cm, 2*cm])
        row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), bg),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LINERIGHT",     (2, 0), (2, 0), 0, WHITE),
        ]))
        story.append(row)

    story.append(Spacer(1, 16))


# ── 06. Recommendations ─────────────────────────────────────────────────────────
def build_recommendations(story, lead, enriched, S):
    section_header(story, "06", "Our Recommendations", S)

    company = lead["company"]
    recs = [
        ("Immediate",          "🔍", ACCENT,
         "Conduct an internal process audit to identify the top 3 workflows consuming the most "
         "manual effort. These are your highest-ROI automation targets."),
        ("30 Days",            "⚡", BLUE,
         f"Deploy a lead intake automation system similar to this report pipeline for {company}. "
         "Personalised first interactions significantly improve conversion rates."),
        ("90 Days",            "🔗", GREEN,
         "Integrate an AI-powered data enrichment layer into your CRM to keep prospect and "
         "client profiles up-to-date automatically."),
        ("Strategic",          "🗺️", ORANGE,
         "Develop an AI adoption roadmap aligned to your 12-month growth goals. SimplifiIQ "
         "can support this journey from strategy through to full deployment."),
    ]

    for horizon, icon, color, text in recs:
        row = Table([[
            Table([[Paragraph(icon, ParagraphStyle("icon", fontName="Helvetica-Bold",
                    fontSize=14, textColor=WHITE, leading=18, alignment=TA_CENTER)),
                    Paragraph(horizon, ParagraphStyle("hz", fontName="Helvetica-Bold",
                    fontSize=8, textColor=colors.HexColor("#CBD5E1"), leading=11,
                    alignment=TA_CENTER))]],
                   colWidths=[2*cm]),
            Paragraph(text, S["body_white"]),
        ]], colWidths=[2.2*cm, W - 4*cm - 2.2*cm])
        row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
            ("BACKGROUND",    (0, 0), (0, -1), color),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(row)
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 16))


# ── 07. Next Steps ──────────────────────────────────────────────────────────────
def build_next_steps(story, lead, S):
    section_header(story, "07", "Next Steps", S)

    story.append(Paragraph(
        f"Thank you for your interest, <b>{lead['name']}</b>. We'd love to explore how "
        f"SimplifiIQ can deliver measurable impact for <b>{lead['company']}</b>.",
        S["body"]
    ))
    story.append(Spacer(1, 10))

    steps = [
        ("1", "Reply to this report email to schedule a 30-minute discovery call.", BLUE),
        ("2", "We'll conduct a deeper workflow audit specific to your operations.", ACCENT),
        ("3", "Receive a tailored automation blueprint with estimated ROI projections.", GREEN),
        ("4", "Begin a pilot project with zero upfront commitment.", ORANGE),
    ]

    for num, text, color in steps:
        row = Table([[
            Paragraph(num, ParagraphStyle("n", fontName="Helvetica-Bold", fontSize=18,
                      textColor=WHITE, leading=22, alignment=TA_CENTER)),
            Paragraph(text, S["body_white"]),
        ]], colWidths=[1.4*cm, W - 4*cm - 1.4*cm])
        row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
            ("BACKGROUND",    (0, 0), (0, -1), color),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(row)
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 20))

    # Contact footer
    footer = Table([[
        Paragraph("📧 career@simplifiiq.com", S["center_white"]),
        Paragraph("|", ParagraphStyle("div", fontName="Helvetica", fontSize=14,
                  textColor=ACCENT, leading=18, alignment=TA_CENTER)),
        Paragraph("🌐 simplifiiq.com", S["center_white"]),
    ]], colWidths=[(W - 4*cm)/3]*3)
    footer.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(footer)


# ── Page Header/Footer ──────────────────────────────────────────────────────────
def on_page(canvas, doc, company):
    canvas.saveState()
    if doc.page > 1:
        # Header
        canvas.setFillColor(NAVY)
        canvas.rect(0, H - 1.1*cm, W, 1.1*cm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.drawString(1.8*cm, H - 0.72*cm, "SimplifiIQ")
        canvas.setFillColor(ACCENT)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(W - 1.8*cm, H - 0.72*cm,
                               f"{company} — Business Audit Report")

        # Footer
        canvas.setFillColor(LIGHT)
        canvas.rect(0, 0, W, 0.9*cm, fill=1, stroke=0)
        canvas.setFillColor(GRAY)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(1.8*cm, 0.32*cm,
                          "Confidential | Generated by SimplifiIQ Research Engine | simplifiiq.com")
        canvas.setFillColor(NAVY)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.drawRightString(W - 1.8*cm, 0.32*cm, f"Page {doc.page}")
    canvas.restoreState()


# ── Main Entry ──────────────────────────────────────────────────────────────────
def generate_pdf_report(lead: dict, enriched: dict, output_path: str):
    company = lead["company"]
    S = styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=1.8*cm,
        bottomMargin=1.6*cm,
        title=f"{company} — Business Audit Report",
        author="SimplifiIQ",
        subject="AI Automation Opportunity Assessment",
    )

    story = []
    build_cover(story, lead, enriched, S)
    build_company_overview(story, lead, enriched, S)
    build_digital_presence(story, lead, enriched, S)
    build_industry_insights(story, lead, enriched, S)
    build_news_section(story, lead, enriched, S)
    build_automation_opportunities(story, lead, enriched, S)
    build_recommendations(story, lead, enriched, S)
    build_next_steps(story, lead, S)

    doc.build(
        story,
        onFirstPage=lambda c, d: on_page(c, d, company),
        onLaterPages=lambda c, d: on_page(c, d, company),
    )
    logger.info(f"📄 PDF saved: {output_path}")
