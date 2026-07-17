"""
PDF Inspection Report Generator (uses reportlab).
Produces a report containing: image, status, confidence, reasons,
severity, suggested actions, timestamp, operator, and supervisor (if verified).
"""
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.core.config import settings


def generate_inspection_pdf(
    output_path: str,
    image_path: str,
    product_name: str,
    status: str,
    confidence: float,
    severity: str,
    reasons: list[str],
    suggested_actions: list[str],
    inspection_time_seconds: float,
    operator_name: str,
    supervisor_name: str | None,
    created_at: datetime,
) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    status_color = colors.HexColor("#1a7f37") if status == "PASS" else colors.HexColor("#c0392b")

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#1f2937"))
    status_style = ParagraphStyle("StatusStyle", parent=styles["Heading1"], textColor=status_color, fontSize=22)

    story = []
    story.append(Paragraph("Inspection Report", title_style))
    story.append(Paragraph(product_name, styles["Heading3"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(status, status_style))
    story.append(Spacer(1, 12))

    if image_path and os.path.exists(image_path):
        story.append(RLImage(image_path, width=100 * mm, height=75 * mm))
        story.append(Spacer(1, 12))

    meta_table_data = [
        ["Confidence", f"{confidence * 100:.1f}%"],
        ["Severity", severity.title()],
        ["Inspection Time", f"{inspection_time_seconds:.2f} seconds"],
        ["Timestamp", created_at.strftime("%Y-%m-%d %H:%M:%S")],
        ["Operator", operator_name],
        ["Supervisor", supervisor_name or "Pending verification"],
    ]
    meta_table = Table(meta_table_data, colWidths=[50 * mm, 100 * mm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Reasons", styles["Heading2"]))
    for r in reasons:
        story.append(Paragraph(f"• {r}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Suggested Actions", styles["Heading2"]))
    for a in suggested_actions:
        story.append(Paragraph(f"• {a}", styles["Normal"]))

    doc.build(story)
    return output_path
