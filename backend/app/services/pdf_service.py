from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
from typing import Dict, Any

class PDFService:
    
    @staticmethod
    def generate_booking_report(booking_data: Dict[str, Any]) -> bytes:
        """
        Generate a professional PDF booking report from provided data
        """
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create document with professional styling
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build story (content)
        story = []
        
        # Add styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2E86AB')
        )
        
        # Header
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_RIGHT
        )
        
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", header_style))
        story.append(Spacer(1, 20))
        
        # Title
        story.append(Paragraph("BOOKING CONFIRMATION", title_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Booking Reference: #{booking_data['booking']['id']}", styles['Heading2']))
        story.append(Spacer(1, 30))
        
        # Booking Details Section
        story.append(Paragraph("Booking Details", heading_style))
        
        booking_table_data = [
            ['Status:', booking_data['booking']['status'].upper()],
            ['Booking Date:', booking_data['booking']['created_at'].strftime('%Y-%m-%d %H:%M')],
            ['Total Amount:', f"Rs.{booking_data['booking']['total_cost']:.2f}"],
            ['Rescheduled:', 'Yes' if booking_data['booking']['rescheduled'] else 'No']
        ]
        
        if booking_data['booking']['rescheduled'] and booking_data['reschedule_history']:
            latest_reschedule = booking_data['reschedule_history'][0]
            booking_table_data.extend([
                ['Originally Booked:', latest_reschedule['original_start_time'].strftime('%Y-%m-%d %H:%M')],
                ['Rescheduled On:', latest_reschedule['created_at'].strftime('%Y-%m-%d %H:%M')]
            ])
        
        booking_table = Table(booking_table_data, colWidths=[2*inch, 3*inch])
        booking_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(booking_table)
        story.append(Spacer(1, 20))
        
        # Event Timing Section
        story.append(Paragraph("Event Timing", heading_style))
        
        timing_data = [
            ['Start Time:', booking_data['booking']['start_time'].strftime('%Y-%m-%d %H:%M')],
            ['End Time:', booking_data['booking']['end_time'].strftime('%Y-%m-%d %H:%M')],
            ['Duration:', f"{booking_data['cost_breakdown']['room_duration']:.1f} hours"]
        ]
        
        timing_table = Table(timing_data, colWidths=[2*inch, 3*inch])
        timing_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(timing_table)
        story.append(Spacer(1, 20))
        
        # Venue & Room Details Section
        story.append(Paragraph("Venue & Room Details", heading_style))
        
        venue_room_data = [
            ['Venue:', booking_data['venue']['name']],
            ['Address:', f"{booking_data['venue']['address']}, {booking_data['venue']['city']}"],
            ['Room:', booking_data['room']['name']],
            ['Room Type:', booking_data['room']['type']],
            ['Capacity:', f"{booking_data['room']['capacity']} people"],
            ['Rate:', f"Rs.{booking_data['room']['rate_per_hour']:.2f}/hour"]
        ]
        
        if booking_data['room']['amenities']:
            venue_room_data.append(['Amenities:', ', '.join(booking_data['room']['amenities'])])
        
        venue_room_table = Table(venue_room_data, colWidths=[2*inch, 3*inch])
        venue_room_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(venue_room_table)
        story.append(Spacer(1, 20))
        
        # Customer Details Section
        story.append(Paragraph("Customer Details", heading_style))
        
        customer_headers = ['Name', 'Phone', 'Address']
        customer_data = [customer_headers]
        
        for customer in booking_data['customers']:
            customer_data.append([
                f"{customer['first_name']} {customer['last_name']}",
                customer['phone'],
                customer['address']
            ])
        
        customer_table = Table(customer_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        customer_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(customer_table)
        story.append(Spacer(1, 20))
        
        # Addons Section (if any)
        if booking_data['addons']:
            story.append(Paragraph("Additional Services", heading_style))
            
            addon_headers = ['Service', 'Quantity', 'Unit Price', 'Subtotal']
            addon_data = [addon_headers]
            total_addons_cost = 0
            
            for addon in booking_data['addons']:
                addon_data.append([
                    addon['name'],
                    str(addon['quantity']),
                    f"Rs.{addon['unit_price']:.2f}",
                    f"Rs.{addon['subtotal']:.2f}"
                ])
                total_addons_cost += addon['subtotal']
            
            addon_data.append(['', '', 'Total:', f"Rs.{total_addons_cost:.2f}"])
            
            addon_table = Table(addon_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
            addon_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('BACKGROUND', (0, -1), (-2, -1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (-2, -1), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(addon_table)
            story.append(Spacer(1, 20))
        
        # Cost Breakdown Section
        story.append(Paragraph("Cost Breakdown", heading_style))
        
        cost_data = [
            ['Room Rental:', f"Rs.{booking_data['cost_breakdown']['room_cost']:.2f}"],
            ['Additional Services:', f"Rs.{booking_data['cost_breakdown']['addons_cost']:.2f}"],
            ['', ''],
            ['TOTAL AMOUNT:', f"Rs.{booking_data['booking']['total_cost']:.2f}"]
        ]
        
        cost_table = Table(cost_data, colWidths=[3*inch, 2*inch])
        cost_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -2), 'Helvetica', 10),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F8F9FA')),
        ]))
        
        story.append(cost_table)
        story.append(Spacer(1, 30))
        
        # Footer Note
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("Thank you for choosing our venue services. For any queries, please contact our support team.", footer_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("This is an computer-generated document and does not require a signature.", footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes