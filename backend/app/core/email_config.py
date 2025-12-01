import os

class EmailSettings:
    def __init__(self):
        self.SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.getenv("EMAIL_SMTP_USERNAME", "")
        self.SMTP_PASSWORD = os.getenv("EMAIL_SMTP_PASSWORD", "")
        self.FROM_EMAIL = os.getenv("EMAIL_FROM_EMAIL", "noreply@hallbookingsystem.com")
        self.FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Hall Booking System")

email_settings = EmailSettings()