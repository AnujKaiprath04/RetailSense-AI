import io
import csv
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportGeneratorEngine:
    """
    Automated PDF, Excel, and CSV Report Generator
    """

    def generate_csv_report(self, data: list) -> str:
        output = io.StringIO()
        if not data:
            return ""
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def generate_excel_report(self, data: list) -> bytes:
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='RetailSense Analytics')
        return output.getvalue()

    def generate_pdf_report(self, title: str, summary_metrics: dict, table_data: list) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        
        story = []
        
        # Header Title
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=12
        )
        story.append(Paragraph(title, title_style))
        story.append(Paragraph("RetailSense AI Enterprise Executive Intelligence Report", styles['SubTitle']))
        story.append(Spacer(1, 15))

        # KPI Summary Table
        kpi_data = [["Metric", "Value"]]
        for k, v in summary_metrics.items():
            kpi_data.append([str(k), str(v)])
            
        t_kpi = Table(kpi_data, colWidths=[250, 250])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1'))
        ]))
        story.append(t_kpi)
        story.append(Spacer(1, 20))

        # Data Table
        if table_data and len(table_data) > 0:
            headers = list(table_data[0].keys())
            t_rows = [headers]
            for row in table_data[:15]:
                t_rows.append([str(row[h]) for h in headers])
                
            t_data = Table(t_rows)
            t_data.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8'))
            ]))
            story.append(t_data)

        doc.build(story)
        pdf_value = buffer.getvalue()
        buffer.close()
        return pdf_value
