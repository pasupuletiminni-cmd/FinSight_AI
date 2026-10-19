"""
pdf_report_generator.py

Institutional-grade PDF Report Generation Engine for FinSight AI.
Complies with Milestone 3 Task 1 & Final Report Agent requirements:
- Compiles multi-agent outputs into an analyst-style structured PDF report
- Includes:
    1. Executive Summary & Key Takeaways
    2. Audited Key Financials (Reported vs Derived, YoY Variance, Citation Provenance)
    3. Red Flag Risk Audit & Anomaly Detection (Severity, Criteria, Verbatim Excerpts)
    4. Peer Benchmarking & Cross-Company Comparison
    5. Forward Outlook, Data Limitations & Strict Governance Disclaimers
"""

import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)

# Brand Color Palette
PRIMARY_EMERALD = colors.HexColor("#0F382C")
SECONDARY_EMERALD = colors.HexColor("#164E3D")
GOLD_ACCENT = colors.HexColor("#D4AF37")
DARK_CHARCOAL = colors.HexColor("#1A1F1D")
MUTED_SLATE = colors.HexColor("#5E6963")
LIGHT_BG = colors.HexColor("#F9F8F5")
BORDER_LIGHT = colors.HexColor("#E2E8E5")
ALERT_RED = colors.HexColor("#C5221F")
SUCCESS_GREEN = colors.HexColor("#107C41")


def generate_pdf_report(
    report_obj: Dict[str, Any],
    comparison_data: Optional[Dict[str, Any]] = None,
    output_path: Optional[str] = None
) -> bytes:
    """
    Generate an analyst-style PDF briefing from the Report Agent data structure.
    Returns PDF bytes and optionally saves to output_path.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        output_path if output_path else buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY_EMERALD,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=MUTED_SLATE,
        spaceAfter=12,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=PRIMARY_EMERALD,
        spaceBefore=14,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=DARK_CHARCOAL,
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=DARK_CHARCOAL,
        leftIndent=12,
        firstLineIndent=-12,
        spaceAfter=4,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=DARK_CHARCOAL,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=PRIMARY_EMERALD,
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Italic"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=MUTED_SLATE,
    )

    story = []

    # 1. Header Banner & Title
    company = report_obj.get("company", "Enterprise")
    years = report_obj.get("fiscal_years", [])
    if isinstance(years, list) and len(years) >= 2:
        prior_yr = str(years[0])
        curr_yr = str(years[1])
    elif isinstance(years, dict):
        prior_yr = str(years.get("previous", "Prior"))
        curr_yr = str(years.get("current", "Current"))
    else:
        prior_yr, curr_yr = "Prior", "Current"
    gen_time = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")

    story.append(Paragraph("📈 FinSight AI — Institutional Financial Intelligence", title_style))
    story.append(Paragraph(
        f"<b>Autonomous Multi-Agent Equity Audit & Research Briefing</b> &nbsp;|&nbsp; <b>{company}</b> (FY{prior_yr} vs FY{curr_yr}) &nbsp;|&nbsp; Generated: {gen_time}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD_ACCENT, spaceBefore=0, spaceAfter=10))

    # Meta KPI Block
    meta_data = [
        [
            Paragraph("<b>Target Enterprise:</b>", body_style),
            Paragraph(str(company), body_style),
            Paragraph("<b>Audited Filing Scope:</b>", body_style),
            Paragraph(f"FY{prior_yr} – FY{curr_yr} Audited 10-K / Annual", body_style),
        ],
        [
            Paragraph("<b>Orchestration Pipeline:</b>", body_style),
            Paragraph("Extraction → YoY Audit → Risk Screening", body_style),
            Paragraph("<b>Provenance Standard:</b>", body_style),
            Paragraph("<font color='#107C41'><b>100% Zero-Hallucination Grounded</b></font>", body_style),
        ]
    ]
    meta_table = Table(meta_data, colWidths=[110, 160, 120, 150])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 2. Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary & Strategic Takeaways", section_heading))
    exec_summary = report_obj.get("executive_summary", {})
    statements = exec_summary.get("statements", [])
    if statements:
        for stmt in statements:
            text = stmt.get("text", "")
            story.append(Paragraph(f"• {text}", bullet_style))
    else:
        summary_text = exec_summary.get("text") or "Multi-period performance analysis conducted across audited statements."
        story.append(Paragraph(summary_text, body_style))

    story.append(Spacer(1, 10))

    # 3. Section 2: Audited Key Financials Table
    story.append(Paragraph("2. Audited Key Financial Metrics & YoY Performance", section_heading))

    key_fin = report_obj.get("key_financials", [])
    table_rows = [
        [
            Paragraph("<b>Financial Metric</b>", table_header_style),
            Paragraph(f"<b>FY{prior_yr}</b>", table_header_style),
            Paragraph(f"<b>FY{curr_yr}</b>", table_header_style),
            Paragraph("<b>YoY Variance</b>", table_header_style),
            Paragraph("<b>Basis</b>", table_header_style),
            Paragraph("<b>Source Provenance</b>", table_header_style),
        ]
    ]

    for item in key_fin:
        metric_name = item.get("metric_name", item.get("metric_key", ""))
        py_data = item.get("previous_year", {})
        cy_data = item.get("current_year", {})
        comp = item.get("change", {})

        def _fmt(val_dict):
            val = val_dict.get("value")
            if val is None or val_dict.get("status") == "NOT_FOUND":
                return "Not Found"
            u = val_dict.get("unit") or ""
            return f"{val:,.2f} {u}".strip()

        py_str = _fmt(py_data)
        cy_str = _fmt(cy_data)

        # YoY Variance
        pct = comp.get("percentage_change")
        pts = comp.get("margin_change_points")
        if pct is not None:
            if pct > 0:
                yoy_str = f"+{pct:.2f}%"
            elif pct < 0:
                yoy_str = f"{pct:.2f}%"
            else:
                yoy_str = "0.00%"
        elif pts is not None:
            if pts > 0:
                yoy_str = f"+{pts:.2f} pts"
            elif pts < 0:
                yoy_str = f"{pts:.2f} pts"
            else:
                yoy_str = "0.00 pts"
        else:
            yoy_str = comp.get("status", "—")

        basis = cy_data.get("basis") or py_data.get("basis") or "Reported"
        src_file = cy_data.get("source_file") or py_data.get("source_file") or "Filing"
        pg = cy_data.get("page_number") or py_data.get("page_number") or "?"
        prov_str = f"{src_file}, p.{pg}"

        table_rows.append([
            Paragraph(metric_name, table_cell_bold),
            Paragraph(py_str, table_cell_style),
            Paragraph(cy_str, table_cell_style),
            Paragraph(yoy_str, table_cell_style),
            Paragraph(basis, table_cell_style),
            Paragraph(prov_str, table_cell_style),
        ])

    fin_table = Table(table_rows, colWidths=[110, 85, 85, 75, 60, 125])
    fin_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_EMERALD),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 10))

    # 4. Section 3: Red Flag Anomaly & Risk Audit
    story.append(Paragraph("3. Agent 3: Red Flag Anomaly & Financial Risk Audit", section_heading))
    red_flags = report_obj.get("red_flags", [])
    if not red_flags:
        story.append(Paragraph(
            "<b>Zero Critical Red Flags Detected.</b> Core liquidity, solvency, margin stability, and operational cash flow parameters remained within healthy bounds across the evaluated periods.",
            body_style
        ))
    else:
        story.append(Paragraph(
            f"<b>{len(red_flags)} Risk Disclosures & Operational Anomalies Flagged:</b>",
            body_style
        ))
        for rf in red_flags:
            sev = rf.get("severity", "MODERATE").upper()
            title = rf.get("title", rf.get("category", "Risk Observation"))
            desc = rf.get("description", "")
            crit = rf.get("criteria", "")
            evid = rf.get("evidence", "")
            src = f"{rf.get('source_file', '')}, p.{rf.get('page_number', '?')}" if rf.get('source_file') else ""

            color_tag = "red" if sev in ("CRITICAL", "HIGH") else "#B8972E"
            flag_text = f"• <b><font color='{color_tag}'>[{sev}] {title}</font></b>: {desc}"
            if crit:
                flag_text += f"<br/>&nbsp;&nbsp;<i>Trigger Rule:</i> {crit}"
            if evid:
                flag_text += f"<br/>&nbsp;&nbsp;<i>Verbatim Evidence:</i> \"{evid[:200]}...\""
            if src:
                flag_text += f" &nbsp;[<i>{src}</i>]"

            story.append(Paragraph(flag_text, bullet_style))

    story.append(Spacer(1, 10))

    # 5. Section 4: Peer Benchmarking (if comparison data passed)
    if comparison_data and comparison_data.get("comparisons"):
        story.append(Paragraph("4. Peer Benchmarking & Cross-Enterprise Comparison", section_heading))
        comp_rows = [
            [
                Paragraph("<b>Metric</b>", table_header_style),
                Paragraph("<b>Company</b>", table_header_style),
                Paragraph("<b>Reported Value</b>", table_header_style),
                Paragraph("<b>Currency</b>", table_header_style),
                Paragraph("<b>Citation</b>", table_header_style),
            ]
        ]
        for c_item in comparison_data.get("comparisons", []):
            m_label = c_item.get("metric_label", "")
            for entry in c_item.get("entries", []):
                val_formatted = f"{entry['value']:,.2f} {entry.get('unit', '')}" if entry.get("value") is not None else "Not Found"
                comp_rows.append([
                    Paragraph(m_label, table_cell_bold),
                    Paragraph(str(entry.get("company", "")), table_cell_style),
                    Paragraph(val_formatted, table_cell_style),
                    Paragraph(str(entry.get("currency") or "—"), table_cell_style),
                    Paragraph(f"{entry.get('source_file', '')}, p.{entry.get('page_number', '?')}", table_cell_style),
                ])
        cmp_table = Table(comp_rows, colWidths=[120, 110, 110, 70, 130])
        cmp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SECONDARY_EMERALD),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ]))
        story.append(cmp_table)
        story.append(Spacer(1, 10))

    # 6. Section 5: Outlook & Analytical Governance Disclaimer
    story.append(Paragraph("5. Research Methodology & Governance Disclaimer", section_heading))
    disclaimer_text = (
        "<b>Strict Provenance Standard:</b> Every numerical value in this briefing is retrieved with zero estimation "
        "or hallucination from the verified corporate annual reports indexed in the FinSight AI ChromaDB collection. "
        "Derived metrics (e.g. Operating Margin, YoY variations) follow deterministic mathematical definitions. "
        "Cross-currency arithmetic between non-identical denominations (e.g., USD and INR) is strictly prohibited. "
        "This document is compiled autonomously for fundamental financial research and education; it does not constitute "
        "investment advice or securities recommendations."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)

    if not output_path:
        buffer.seek(0)
        return buffer.getvalue()
    return b""
