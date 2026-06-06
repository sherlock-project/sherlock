"""
PDF Raporlama Modulu
ReportLab ile PDF export
"""

from pathlib import Path
from typing import List
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from sherlock_project.result import QueryResult


class PDFReporter:
    """PDF rapor uretici"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f538d'),
            alignment=TA_CENTER,
            spaceAfter=30
        )

    def generate(
        self,
        username: str,
        results: List[QueryResult],
        output_path: str
    ) -> str:
        """
        PDF raporu olustur

        Args:
            username: Aranan kullanici adi
            results: Tarama sonuclari
            output_path: Cikis dosya yolu

        Returns:
            Olusturulan dosya yolu
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        elements = []

        # Baslik
        title = Paragraph(f'Sherlock Report: {username}', self.title_style)
        elements.append(title)

        # Tarih
        date_text = Paragraph(
            f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            self.styles['Normal']
        )
        elements.append(date_text)
        elements.append(Spacer(1, 0.2 * inch))

        # Ozet
        found_count = sum(1 for r in results if r.status.value == 'Claimed')
        summary = Paragraph(
            f'Found {found_count} accounts out of {len(results)} sites checked.',
            self.styles['Normal']
        )
        elements.append(summary)
        elements.append(Spacer(1, 0.3 * inch))

        # Tablo verisi
        table_data = [['Site', 'Status', 'Response Time', 'URL']]
        for result in results:
            if result.status.value == 'Claimed':
                table_data.append([
                    result.site_name,
                    'Found',
                    f'{result.query_time:.2f}s',
                    result.site_url_user
                ])

        # Tablo
        if len(table_data) > 1:
            table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f538d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            elements.append(table)
        else:
            no_results = Paragraph('No accounts found.', self.styles['Normal'])
            elements.append(no_results)

        # PDF olustur
        doc.build(elements)
        return output_path
