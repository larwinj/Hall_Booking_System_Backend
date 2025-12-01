import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import os
from typing import List, Optional
from app.core.email_config import email_settings

class EmailService:
        
    @staticmethod
    def _render_template(template_name: str, context: dict) -> str:
        """Render HTML email template with context"""
        template_path = os.path.join("app/templates/emails", template_name)
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        
        template = Template(template_content)
        return template.render(**context)
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        cc_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send email using SMTP
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{email_settings.FROM_NAME} <{email_settings.FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(email_settings.SMTP_SERVER, email_settings.SMTP_PORT) as server:
                server.starttls()
                server.login(email_settings.SMTP_USERNAME, email_settings.SMTP_PASSWORD)
                
                recipients = [to_email]
                if cc_emails:
                    recipients.extend(cc_emails)
                
                server.send_message(msg)
                print(f"Email sent successfully to {to_email}")
                return True
                
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    async def send_booking_confirmation(
        customer_email: str,
        customer_name: str,
        booking_id: int,
        venue_name: str,
        room_name: str,
        start_time: str,
        end_time: str,
        total_cost: float,
        status: str = "confirmed"
    ) -> bool:
        """Send booking confirmation email"""
        context = {
            "customer_name": customer_name,
            "booking_id": booking_id,
            "venue_name": venue_name,
            "room_name": room_name,
            "start_time": start_time,
            "end_time": end_time,
            "total_cost": total_cost,
            "status": status
        }
        
        html_content = EmailService._render_template("booking_confirmation.html", context)
        subject = f"Booking Confirmed - #{booking_id}"
        
        return await EmailService.send_email(customer_email, subject, html_content)
    
    @staticmethod
    async def send_booking_rescheduled(
        customer_email: str,
        customer_name: str,
        booking_id: int,
        venue_name: str,
        room_name: str,
        start_time: str,
        end_time: str,
        total_cost: float,
        original_start_time: Optional[str] = None,
        original_end_time: Optional[str] = None,
        price_difference: float = 0
    ) -> bool:
        """Send booking rescheduled email"""
        context = {
            "customer_name": customer_name,
            "booking_id": booking_id,
            "venue_name": venue_name,
            "room_name": room_name,
            "start_time": start_time,
            "end_time": end_time,
            "total_cost": total_cost,
            "original_start_time": original_start_time,
            "original_end_time": original_end_time,
            "price_difference": price_difference
        }
        
        html_content = EmailService._render_template("booking_rescheduled.html", context)
        subject = f"Booking Rescheduled - #{booking_id}"
        
        return await EmailService.send_email(customer_email, subject, html_content)
    
    @staticmethod
    async def send_booking_cancelled(
        customer_email: str,
        customer_name: str,
        booking_id: int,
        venue_name: str,
        room_name: str,
        start_time: str,
        end_time: str,
        reason: Optional[str] = None,
        refund_amount: float = 0,
        refund_policy: str = ""
    ) -> bool:
        """Send booking cancellation email"""
        context = {
            "customer_name": customer_name,
            "booking_id": booking_id,
            "venue_name": venue_name,
            "room_name": room_name,
            "start_time": start_time,
            "end_time": end_time,
            "reason": reason,
            "refund_amount": refund_amount,
            "refund_policy": refund_policy
        }
        
        html_content = EmailService._render_template("booking_cancelled.html", context)
        subject = f"Booking Cancelled - #{booking_id}"
        
        return await EmailService.send_email(customer_email, subject, html_content)
    
    @staticmethod
    async def send_custom_notification(
        customer_email: str,
        customer_name: str,
        subject: str,
        message: str,
        booking_id: Optional[int] = None
    ) -> bool:
        """Send custom notification email"""
        context = {
            "customer_name": customer_name,
            "message": message,
            "booking_id": booking_id
        }
        
        html_content = EmailService._render_template("custom_notification.html", context)
        
        return await EmailService.send_email(customer_email, subject, html_content)