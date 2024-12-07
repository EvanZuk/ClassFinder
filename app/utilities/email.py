import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from app.utilities.env import devmode
from app import app

emailids = {}
resetemailids = {}
emailconfig = {
    "server": os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
    "port": os.environ.get('EMAIL_PORT', 587),
    "username": os.environ.get('EMAIL_USERNAME'),
    "password": os.environ.get('EMAIL_PASSWORD'),
    "from": os.environ.get('EMAIL_FROM')
}


def send_email(email: str, subject: str, message: str):
    """
    Send an email
    """
    if devmode:
        app.logger.info(f"An email was sent to {email} with subject {subject} and message {message}")
        return
    msg = MIMEMultipart()
    msg['From'] = emailconfig['from']
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP(emailconfig['server'], emailconfig['port'])
    server.starttls()
    server.login(emailconfig['username'], emailconfig['password'])
    server.sendmail(emailconfig['from'], email, msg.as_string())
    server.quit()
    return True

def create_email_id(email: str):
    """
    Create an email id for an email
    """
    emailid = os.urandom(30).hex()
    emailids[emailid] = email
    return emailid

def check_email_id(emailid: str):
    """
    Check if an email id is valid and returns the email
    """
    if emailid in emailids:
        return emailids[emailid]
    return None

def create_reset_email_id(email: str):
    """
    Create a reset password email id for an email
    """
    emailid = os.urandom(30).hex()
    resetemailids[emailid] = email
    return emailid

def check_reset_email_id(emailid: str):
    """
    Check if a reset password email id is valid and returns the email
    """
    if emailid in resetemailids:
        return resetemailids[emailid]
    return None