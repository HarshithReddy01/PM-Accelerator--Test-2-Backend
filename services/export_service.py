import json
import csv
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from models import WeatherRecord
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

class ExportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    def export_to_json(self, records: List[WeatherRecord]) -> str:
        """
        Export weather records to JSON format
        """
        try:
            data = []
            for record in records:
                record_data = {
                    'id': record.id,
                    'location': record.location,
                    'start_date': record.start_date,
                    'end_date': record.end_date,
                    'latitude': record.latitude,
                    'longitude': record.longitude,
                    'created_at': record.created_at.isoformat() if record.created_at else None,
                    'updated_at': record.updated_at.isoformat() if record.updated_at else None,
                    'temperature_data': record.temperature_data
                }
                data.append(record_data)
            
            return json.dumps(data, indent=2, default=str)
            
        except Exception as e:
            raise Exception(f"JSON export error: {str(e)}")
    
    def export_to_csv(self, records: List[WeatherRecord]) -> str:
        """
        Export weather records to CSV format
        """
        try:
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'Location', 'Start Date', 'End Date', 
                'Latitude', 'Longitude', 'Created At', 'Updated At',
                'Current Temp', 'Current Humidity', 'Forecast Count'
            ])
            
            # Write data rows
            for record in records:
                current_temp = "N/A"
                current_humidity = "N/A"
                forecast_count = "N/A"
                
                if record.temperature_data:
                    if 'current' in record.temperature_data:
                        current = record.temperature_data['current']
                        if 'main' in current:
                            current_temp = f"{current['main'].get('temp', 'N/A')}°C"
                            current_humidity = f"{current['main'].get('humidity', 'N/A')}%"
                    
                    if 'forecast' in record.temperature_data:
                        forecast = record.temperature_data['forecast']
                        if 'list' in forecast:
                            forecast_count = len(forecast['list'])
                
                writer.writerow([
                    record.id,
                    record.location,
                    record.start_date,
                    record.end_date,
                    record.latitude,
                    record.longitude,
                    record.created_at.isoformat() if record.created_at else "N/A",
                    record.updated_at.isoformat() if record.updated_at else "N/A",
                    current_temp,
                    current_humidity,
                    forecast_count
                ])
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"CSV export error: {str(e)}")
    
    def export_to_xml(self, records: List[WeatherRecord]) -> str:
        """
        Export weather records to XML format
        """
        try:
            root = ET.Element("weather_records")
            root.set("export_date", datetime.now().isoformat())
            root.set("total_records", str(len(records)))
            
            for record in records:
                record_elem = ET.SubElement(root, "record")
                
                # Basic record info
                ET.SubElement(record_elem, "id").text = str(record.id)
                ET.SubElement(record_elem, "location").text = record.location
                ET.SubElement(record_elem, "start_date").text = record.start_date
                ET.SubElement(record_elem, "end_date").text = record.end_date
                ET.SubElement(record_elem, "latitude").text = str(record.latitude)
                ET.SubElement(record_elem, "longitude").text = str(record.longitude)
                
                # Timestamps
                created_elem = ET.SubElement(record_elem, "created_at")
                if record.created_at:
                    created_elem.text = record.created_at.isoformat()
                
                updated_elem = ET.SubElement(record_elem, "updated_at")
                if record.updated_at:
                    updated_elem.text = record.updated_at.isoformat()
                
                # Weather data summary
                if record.temperature_data:
                    weather_elem = ET.SubElement(record_elem, "weather_summary")
                    
                    if 'current' in record.temperature_data:
                        current = record.temperature_data['current']
                        if 'main' in current:
                            current_elem = ET.SubElement(weather_elem, "current_weather")
                            ET.SubElement(current_elem, "temperature").text = str(current['main'].get('temp', 'N/A'))
                            ET.SubElement(current_elem, "humidity").text = str(current['main'].get('humidity', 'N/A'))
                    
                    if 'forecast' in record.temperature_data:
                        forecast = record.temperature_data['forecast']
                        if 'list' in forecast:
                            forecast_elem = ET.SubElement(weather_elem, "forecast")
                            ET.SubElement(forecast_elem, "total_periods").text = str(len(forecast['list']))
            
            # Create XML string with proper formatting
            ET.indent(root, space="  ")
            return ET.tostring(root, encoding='unicode', method='xml')
            
        except Exception as e:
            raise Exception(f"XML export error: {str(e)}")
    
    def export_to_pdf(self, records: List[WeatherRecord]) -> bytes:
        """
        Export weather records to PDF format
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            title = Paragraph("Weather Records Report", title_style)
            elements.append(title)
            
            # Summary
            summary_style = self.styles['Normal']
            summary_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>Total Records: {len(records)}"
            summary = Paragraph(summary_text, summary_style)
            elements.append(summary)
            elements.append(Spacer(1, 20))
            
            # Table data
            table_data = [['ID', 'Location', 'Date Range', 'Coordinates', 'Created']]
            
            for record in records:
                date_range = f"{record.start_date} to {record.end_date}"
                coordinates = f"{record.latitude:.4f}, {record.longitude:.4f}"
                created = record.created_at.strftime('%Y-%m-%d') if record.created_at else "N/A"
                
                table_data.append([
                    str(record.id),
                    record.location,
                    date_range,
                    coordinates,
                    created
                ])
            
            # Create table
            table = Table(table_data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1.5*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # Weather details for each record
            for record in records:
                if record.temperature_data:
                    elements.append(Paragraph(f"<b>Record {record.id} - {record.location}</b>", self.styles['Heading2']))
                    
                    if 'current' in record.temperature_data:
                        current = record.temperature_data['current']
                        if 'main' in current:
                            current_text = f"Current Temperature: {current['main'].get('temp', 'N/A')}°C<br/>"
                            current_text += f"Humidity: {current['main'].get('humidity', 'N/A')}%"
                            elements.append(Paragraph(current_text, self.styles['Normal']))
                    
                    if 'forecast' in record.temperature_data:
                        forecast = record.temperature_data['forecast']
                        if 'list' in forecast:
                            forecast_text = f"Forecast Periods: {len(forecast['list'])}"
                            elements.append(Paragraph(forecast_text, self.styles['Normal']))
                    
                    elements.append(Spacer(1, 10))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"PDF export error: {str(e)}")
    
    def export_to_markdown(self, records: List[WeatherRecord]) -> str:
        """
        Export weather records to Markdown format
        """
        try:
            markdown = []
            
            # Header
            markdown.append("# Weather Records Report")
            markdown.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            markdown.append(f"**Total Records:** {len(records)}")
            markdown.append("")
            
            # Summary table
            markdown.append("## Records Summary")
            markdown.append("")
            markdown.append("| ID | Location | Date Range | Coordinates | Created |")
            markdown.append("|----|----------|------------|-------------|---------|")
            
            for record in records:
                date_range = f"{record.start_date} to {record.end_date}"
                coordinates = f"{record.latitude:.4f}, {record.longitude:.4f}"
                created = record.created_at.strftime('%Y-%m-%d') if record.created_at else "N/A"
                
                markdown.append(f"| {record.id} | {record.location} | {date_range} | {coordinates} | {created} |")
            
            markdown.append("")
            
            # Detailed information
            markdown.append("## Detailed Information")
            markdown.append("")
            
            for record in records:
                markdown.append(f"### Record {record.id} - {record.location}")
                markdown.append("")
                markdown.append(f"- **Location:** {record.location}")
                markdown.append(f"- **Date Range:** {record.start_date} to {record.end_date}")
                markdown.append(f"- **Coordinates:** {record.latitude:.4f}, {record.longitude:.4f}")
                markdown.append(f"- **Created:** {record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else 'N/A'}")
                markdown.append(f"- **Updated:** {record.updated_at.strftime('%Y-%m-%d %H:%M:%S') if record.updated_at else 'N/A'}")
                markdown.append("")
                
                if record.temperature_data:
                    markdown.append("#### Weather Data")
                    markdown.append("")
                    
                    if 'current' in record.temperature_data:
                        current = record.temperature_data['current']
                        if 'main' in current:
                            markdown.append(f"- **Current Temperature:** {current['main'].get('temp', 'N/A')}°C")
                            markdown.append(f"- **Humidity:** {current['main'].get('humidity', 'N/A')}%")
                            markdown.append("")
                    
                    if 'forecast' in record.temperature_data:
                        forecast = record.temperature_data['forecast']
                        if 'list' in forecast:
                            markdown.append(f"- **Forecast Periods:** {len(forecast['list'])}")
                            markdown.append("")
                
                markdown.append("---")
                markdown.append("")
            
            return "\n".join(markdown)
            
        except Exception as e:
            raise Exception(f"Markdown export error: {str(e)}")
    
    def export_records(self, db: Session, format_type: str) -> Tuple[bool, Any, Optional[str]]:
        """
        Export all weather records in the specified format
        """
        try:
            records = db.query(WeatherRecord).all()
            
            if format_type == 'json':
                data = self.export_to_json(records)
                return True, data, None
            elif format_type == 'csv':
                data = self.export_to_csv(records)
                return True, data, None
            elif format_type == 'xml':
                data = self.export_to_xml(records)
                return True, data, None
            elif format_type == 'pdf':
                data = self.export_to_pdf(records)
                return True, data, None
            elif format_type == 'markdown':
                data = self.export_to_markdown(records)
                return True, data, None
            else:
                return False, None, f"Unsupported export format: {format_type}"
                
        except Exception as e:
            return False, None, f"Export error: {str(e)}"
