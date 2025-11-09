import smtplib
from email.message import EmailMessage
from ..config import settings
import logging

def send_email(to: str, subject: str, html: str):
    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = settings.SMTP_FROM
    message['To'] = to
    message.set_content("This is an HTML email. Please view in an HTML-compatible client.")
    message.add_alternative(html, subtype='html')

    try:
        if settings.SMTP_PORT == 465:  
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USER:
                    server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(message)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                if settings.SMTP_USER:
                    server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(message)
        logging.info(f"Email sent to {to} with subject '{subject}'")
   
    except Exception as e:
        logging.error(f"Failed to send email to {to}: {e}")
