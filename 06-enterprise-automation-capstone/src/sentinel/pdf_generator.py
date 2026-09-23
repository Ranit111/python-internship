"""
Automated PDF Executive Report generator using ReportLab.
"""

from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFReportGenerator:
    """Builds professional, styled enterprise PDF health and telemetry reports."""

    def __init__(self, output_path: str | Path, company_name: str = "Enterprise Systems") -> None:
        self.output_path = Path(output_path)
        self.company_name = company_name

    def build_report(self, telemetry: Dict[str, Any], evaluation: Dict[str, Any]) -> Path:
        """Assembles and writes publication-grade PDF document."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "SubTitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=12,
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )
        bold_body = ParagraphStyle(
            "BoldBody",
            parent=body_style,
            fontName="Helvetica-Bold",
        )

        elements = []

        # 1. Header & Title Banner
        elements.append(Paragraph(f"<b>{self.company_name}</b>", subtitle_style))
        elements.append(Paragraph("Executive System Health & Infrastructure Audit", title_style))
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        elements.append(Paragraph(f"Generated at: {now_str} | Status: <b>{evaluation.get('overall_status')}</b>", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284c7"), spaceAfter=14))

        # 2. Executive Summary Box Table
        status_color = colors.HexColor("#16a34a") if evaluation.get("overall_status") == "OPTIMAL" else (
            colors.HexColor("#ea580c") if evaluation.get("overall_status") == "WARNING" else colors.HexColor("#dc2626")
        )
        summary_data = [
            [
                Paragraph("<b>Health Score</b>", bold_body),
                Paragraph(f"<b><font size=14 color='{status_color.hexval()}'>{evaluation.get('health_score')}/100</font></b>", bold_body),
                Paragraph("<b>Audit Grade</b>", bold_body),
                Paragraph(f"<b>{evaluation.get('grade')}</b>", bold_body),
            ],
            [
                Paragraph("<b>Active Warnings</b>", body_style),
                Paragraph(str(evaluation.get("warnings_count", 0)), body_style),
                Paragraph("<b>Critical Outages</b>", body_style),
                Paragraph(str(evaluation.get("critical_count", 0)), body_style),
            ],
        ]
        summary_table = Table(summary_data, colWidths=[110, 150, 110, 160])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 10))

        # 3. Hardware Metrics Table
        sys_data = telemetry.get("system", {})
        cpu = sys_data.get("cpu", {})
        mem = sys_data.get("memory", {})
        disk = sys_data.get("disk", {})
        os_info = sys_data.get("os", {})

        elements.append(Paragraph("Host Machine & Resource Allocation", h2_style))
        hw_data = [
            [Paragraph("Resource Component", bold_body), Paragraph("Utilization", bold_body), Paragraph("Capacity / Metrics", bold_body), Paragraph("Status", bold_body)],
            [Paragraph("CPU Core Usage", body_style), Paragraph(f"{cpu.get('usage_percent')}%", body_style), Paragraph(f"{cpu.get('physical_cores')} Physical / {cpu.get('logical_cores')} Logical", body_style), Paragraph("Nominal", body_style)],
            [Paragraph("Memory (RAM)", body_style), Paragraph(f"{mem.get('usage_percent')}%", body_style), Paragraph(f"{mem.get('used_gb')} GB used of {mem.get('total_gb')} GB", body_style), Paragraph("Nominal" if mem.get('usage_percent', 0) < 80 else "Elevated", body_style)],
            [Paragraph("Disk Storage", body_style), Paragraph(f"{disk.get('usage_percent')}%", body_style), Paragraph(f"{disk.get('free_gb')} GB free of {disk.get('total_gb')} GB", body_style), Paragraph("Nominal" if disk.get('usage_percent', 0) < 85 else "Warning", body_style)],
            [Paragraph("Host Platform", body_style), Paragraph(os_info.get("system", "N/A"), body_style), Paragraph(f"{os_info.get('release')} ({os_info.get('machine')})", body_style), Paragraph(f"Python {os_info.get('python_version')}", body_style)],
        ]
        hw_table = Table(hw_data, colWidths=[140, 90, 200, 100])
        hw_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(hw_table)
        elements.append(Spacer(1, 10))

        # 4. Remote Endpoints Health
        endpoints = telemetry.get("endpoints", [])
        if endpoints:
            elements.append(Paragraph("Remote Services & API Endpoint Health", h2_style))
            ep_data = [
                [Paragraph("Service Name", bold_body), Paragraph("Status Code", bold_body), Paragraph("Response Latency", bold_body), Paragraph("Health", bold_body)],
            ]
            for ep in endpoints:
                ep_stat = "OK" if ep.get("is_healthy") else "FAILED"
                ep_data.append([
                    Paragraph(ep.get("name", ""), body_style),
                    Paragraph(str(ep.get("status_code", 0)), body_style),
                    Paragraph(f"{ep.get('latency_ms', 0)} ms", body_style),
                    Paragraph(ep_stat, bold_body if not ep.get("is_healthy") else body_style),
                ])
            ep_table = Table(ep_data, colWidths=[180, 90, 130, 130])
            ep_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(ep_table)
            elements.append(Spacer(1, 10))

        # 5. Anomalies and Recommendations
        anomalies = evaluation.get("anomalies", [])
        elements.append(Paragraph("Action Items & Incident Log", h2_style))
        if not anomalies:
            elements.append(Paragraph("✅ <i>No anomalies or SLA threshold violations detected. All systems operating within baseline parameters.</i>", body_style))
        else:
            for idx, a in enumerate(anomalies, 1):
                color_tag = "red" if a.get("severity") == "CRITICAL" else "orange"
                elements.append(Paragraph(
                    f"<b>{idx}. [<font color='{color_tag}'>{a.get('severity')}</font>] {a.get('component')}</b>: {a.get('message')}",
                    body_style,
                ))

        # Build Document
        doc.build(elements)
        return self.output_path
