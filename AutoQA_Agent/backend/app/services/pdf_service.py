import io
import logging
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from app.schemas.analysis import RepositoryAnalysisReport

logger = logging.getLogger(__name__)

# ── Colour palette ─────────────────────────────────────────────────────────────
DARK_BG = colors.HexColor("#0F172A")
ACCENT  = colors.HexColor("#06B6D4")
ACCENT2 = colors.HexColor("#6366F1")
LIGHT   = colors.HexColor("#F1F5F9")
MID     = colors.HexColor("#94A3B8")
WHITE   = colors.white
SUCCESS = colors.HexColor("#10B981")
WARNING = colors.HexColor("#F59E0B")
DANGER  = colors.HexColor("#EF4444")
GET_COLOR    = colors.HexColor("#10B981")
POST_COLOR   = colors.HexColor("#F59E0B")
PUT_COLOR    = colors.HexColor("#3B82F6")
DELETE_COLOR = colors.HexColor("#EF4444")


def _method_color(method: str) -> colors.Color:
    m = method.upper()
    return {
        "GET": GET_COLOR,
        "POST": POST_COLOR,
        "PUT": PUT_COLOR,
        "PATCH": PUT_COLOR,
        "DELETE": DELETE_COLOR,
    }.get(m, ACCENT2)


def _confidence_color(score: float) -> colors.Color:
    if score >= 80:
        return SUCCESS
    if score >= 60:
        return WARNING
    return DANGER


def generate_pdf(report: RepositoryAnalysisReport) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"AutoQA Report – {report.repository_name}",
    )

    styles = getSampleStyleSheet()
    W = A4[0] - 36 * mm  # usable width

    # ── Custom styles ──────────────────────────────────────────────────────────
    h1 = ParagraphStyle("H1", fontSize=22, textColor=WHITE, spaceAfter=4,
                        fontName="Helvetica-Bold", alignment=TA_LEFT)
    h2 = ParagraphStyle("H2", fontSize=14, textColor=ACCENT, spaceAfter=3,
                        fontName="Helvetica-Bold", spaceBefore=10)
    h3 = ParagraphStyle("H3", fontSize=11, textColor=LIGHT, spaceAfter=2,
                        fontName="Helvetica-Bold")
    body = ParagraphStyle("Body", fontSize=9, textColor=LIGHT, leading=14,
                          spaceAfter=4, fontName="Helvetica")
    mono = ParagraphStyle("Mono", fontSize=8, textColor=ACCENT, leading=12,
                          fontName="Courier")
    mid_style = ParagraphStyle("Mid", fontSize=8, textColor=MID,
                               fontName="Helvetica")
    step_style = ParagraphStyle("Step", fontSize=9, textColor=LIGHT, leading=14,
                                leftIndent=10, fontName="Helvetica")
    label = ParagraphStyle("Label", fontSize=7, textColor=MID,
                           fontName="Helvetica-Bold", spaceBefore=2)
    evidence_style = ParagraphStyle("Evidence", fontSize=8, textColor=ACCENT,
                                    leading=12, leftIndent=14, fontName="Courier")

    story = []

    # ── Header banner ──────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("🔍 AutoQA Agent", h1),
        Paragraph(f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", mid_style),
    ]]
    header_table = Table(header_data, colWidths=[W * 0.7, W * 0.3])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (0, -1), 14),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))

    # ── Repo name & URL ────────────────────────────────────────────────────────
    story.append(Paragraph(report.repository_name, h2))
    story.append(Paragraph(report.repository_url, mono))
    story.append(HRFlowable(width=W, color=ACCENT, thickness=0.5, spaceAfter=8))

    # ── Stats row ──────────────────────────────────────────────────────────────
    confidence = report.confidence_score
    conf_label = f"{confidence:.0f}%" if confidence is not None else "N/A"
    stats = [
        ("📁 Files", str(report.number_of_files)),
        ("🔌 APIs", str(report.number_of_apis_discovered)),
        ("🌿 Branch", report.metadata.get("default_branch") or "N/A"),
        ("📂 Dirs", str(report.project_structure_summary.directories)),
        ("🎯 Confidence", conf_label),
    ]
    stat_cells = [[Paragraph(f'<font color="#94A3B8" size="7">{k}</font><br/>'
                             f'<font size="14"><b>{v}</b></font>', body) for k, v in stats]]
    stat_table = Table(stat_cells, colWidths=[W / 5] * 5)
    stat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1E293B")),
        ("BOX", (0, 0), (-1, -1), 0.5, ACCENT2),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#334155")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 10))

    # ── Low-confidence warning ─────────────────────────────────────────────────
    if confidence is not None and confidence < 70:
        warn_data = [[Paragraph(
            f'⚠️  <b>Low Confidence Analysis ({confidence:.0f}%)</b> — '
            'Limited evidence found. Manual review recommended.',
            ParagraphStyle("Warn", fontSize=9, textColor=WARNING,
                           fontName="Helvetica-Bold", leading=14)
        )]]
        warn_table = Table(warn_data, colWidths=[W])
        warn_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1C1400")),
            ("BOX", (0, 0), (-1, -1), 1, WARNING),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ]))
        story.append(warn_table)
        story.append(Spacer(1, 8))

    # ── README Summary ─────────────────────────────────────────────────────────
    if report.readme_summary:
        story.append(Paragraph("📖 README Summary (Local Analysis)", h2))
        story.append(Paragraph(report.readme_summary, body))
        story.append(HRFlowable(width=W, color=ACCENT, thickness=0.5, spaceAfter=6))

    # ── AI Explanation (Groq) ──────────────────────────────────────────────────
    ai = report.ai_explanation or {}
    if ai:
        story.append(Paragraph("🤖 AI Analysis (Groq · llama-3.1-8b-instant)", h2))

        if ai.get("project_overview"):
            story.append(Paragraph("Project Overview", h3))
            story.append(Paragraph(ai["project_overview"], body))
            story.append(Spacer(1, 4))

        if ai.get("use_case"):
            story.append(Paragraph(f"Use Case: {ai['use_case']}", mid_style))
            story.append(Spacer(1, 4))

        if ai.get("complexity_level"):
            story.append(Paragraph(f"Complexity: {ai['complexity_level']}", mid_style))
            story.append(Spacer(1, 6))

        if ai.get("workflow"):
            story.append(Paragraph("Workflow", h3))
            for step in ai["workflow"]:
                story.append(Paragraph(f"• {step}", step_style))
            story.append(Spacer(1, 4))

        if ai.get("key_technologies"):
            story.append(Paragraph("Key Technologies", h3))
            for tech, desc in ai["key_technologies"].items():
                story.append(Paragraph(f"<b>{tech}</b>: {desc}", body))
            story.append(Spacer(1, 4))

        if ai.get("api_summary"):
            story.append(Paragraph("API Summary", h3))
            story.append(Paragraph(ai["api_summary"], body))

        story.append(HRFlowable(width=W, color=ACCENT2, thickness=0.5, spaceAfter=6))

    # ── Detected Features ──────────────────────────────────────────────────────
    if report.detected_features:
        story.append(Paragraph("🔎 Detected Features", h2))
        for feature in report.detected_features:
            story.append(Paragraph(f"<b>{feature.name}</b>", h3))
            for ev in feature.evidence:
                story.append(Paragraph(f"  › {ev}", evidence_style))
            story.append(Spacer(1, 4))
        story.append(HRFlowable(width=W, color=ACCENT, thickness=0.5, spaceAfter=6))

    # ── Architecture Notes ─────────────────────────────────────────────────────
    if report.architecture_notes:
        story.append(Paragraph("🏗 Architecture Notes (Ollama + Groq)", h2))
        story.append(Paragraph(report.architecture_notes, body))
        story.append(HRFlowable(width=W, color=ACCENT, thickness=0.5, spaceAfter=6))

    # ── Technology Stack ───────────────────────────────────────────────────────
    tech = report.technology_stack
    story.append(Paragraph("🛠 Technology Stack", h2))
    stack_data = [
        [Paragraph("<b>Category</b>", label), Paragraph("<b>Technologies</b>", label)],
        ["Frontend",  ", ".join(tech.frontend)  or "—"],
        ["Backend",   ", ".join(tech.backend)   or "—"],
        ["Languages", ", ".join(tech.languages) or "—"],
        ["Databases", ", ".join(tech.databases) or "—"],
        ["Frameworks", ", ".join(tech.frameworks) or "—"],
    ]
    stack_table = Table(stack_data, colWidths=[W * 0.28, W * 0.72])
    stack_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#0F172A")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0F172A"), colors.HexColor("#1E293B")]),
        ("TEXTCOLOR", (0, 0), (-1, -1), LIGHT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, ACCENT),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#334155")),
    ]))
    story.append(stack_table)
    story.append(Spacer(1, 10))

    # ── Module Summaries ───────────────────────────────────────────────────────
    if report.module_summaries:
        story.append(Paragraph("📦 Module Summaries (Local Analysis)", h2))
        for mod_name, mod_summary in report.module_summaries.items():
            story.append(Paragraph(f"<b>{mod_name}/</b> — {mod_summary}", body))
        story.append(Spacer(1, 8))

    # ── API Inventory ──────────────────────────────────────────────────────────
    if report.api_inventory:
        story.append(Paragraph("🔌 API Inventory", h2))
        api_header = [
            Paragraph("<b>Method</b>", label),
            Paragraph("<b>Path</b>", label),
            Paragraph("<b>Framework</b>", label),
            Paragraph("<b>File</b>", label),
            Paragraph("<b>Line</b>", label),
        ]
        api_rows = [api_header]
        for ep in report.api_inventory:
            mc = _method_color(ep.method)
            api_rows.append([
                Paragraph(f'<font color="{mc.hexval()}">{ep.method}</font>', mono),
                Paragraph(ep.path, mono),
                Paragraph(ep.framework, body),
                Paragraph(ep.file[-40:] if len(ep.file) > 40 else ep.file, mid_style),
                Paragraph(str(ep.line_number or "—"), mid_style),
            ])
        api_table = Table(api_rows, colWidths=[W*0.1, W*0.22, W*0.16, W*0.42, W*0.1])
        api_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0F172A"), colors.HexColor("#1E293B")]),
            ("TEXTCOLOR", (0, 0), (-1, -1), LIGHT),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("BOX", (0, 0), (-1, -1), 0.5, ACCENT),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#334155")),
        ]))
        story.append(api_table)
        story.append(Spacer(1, 8))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width=W, color=ACCENT2, thickness=0.5))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Report ID: {report.analysis_id}  •  AutoQA Agent  •  {datetime.utcnow().strftime('%Y-%m-%d')}",
        mid_style,
    ))

    doc.build(story)
    return buffer.getvalue()
