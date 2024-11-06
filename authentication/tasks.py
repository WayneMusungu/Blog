from time import sleep
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(name="welcome_email")
def send_thank_you_email(user_email):
    logger.info("Started sending thank you email to %s", user_email)
    
    try:
        sleep(30)  # Simulating a delay
        subject = "Thank You for Logging In!"
        message = "We appreciate your continued engagement with our platform!"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]

        send_mail(subject, message, from_email, recipient_list)
        logger.info("Successfully sent thank you email to %s", user_email)
        
        return "Task Done!"
    
    except Exception as e:
        logger.error("Failed to send thank you email to %s: %s", user_email, str(e))