from django.conf import settings
from django.core.mail import send_mail
import logging

# Get logger instance
logger = logging.getLogger(__name__)

def send_account_activation_email(email, email_token):
    try:
        subject = 'Your account activation email'
        email_from = settings.EMAIL_HOST_USER
        message = f'Hi, click on the link to activate your account http://127.0.0.1:8000/accounts/activate/{email_token}'
        send_mail(subject, message, email_from, [email])
    except Exception as e:
        # Log the error message
        logger.error(f"Error sending activation email to {email}: {e}")