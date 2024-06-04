import json
import schedule
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load tickets from a JSON file
with open('tickets.json') as f:
    tickets = json.load(f)

# Define priority to resolution time mapping
priority_to_resolution = {
    "low": timedelta(hours=8),
    "medium": timedelta(hours=6),
    "high": timedelta(hours=4),
    "critical": timedelta(hours=2)
}

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'mydummymailacnt@gmail.com'
SMTP_PASSWORD = 'OKOK2001'
EMAIL_FROM = 'mydummymailacnt@gmail.com'
EMAIL_TO = 'keerthisathya20@gmail.com'  
EMAIL_SUBJECT = 'Ticket Reminder'

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = to

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable smtplib debug output
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, [to], msg.as_string())
            logging.info(f"Email sent to {to}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def validate_ticket(ticket):
    required_keys = {"id": str, "priority": str, "created_time": str}
    if not all(key in ticket for key in required_keys):
        return False
    for key, expected_type in required_keys.items():
        if not isinstance(ticket[key], expected_type):
            return False
    if ticket["priority"] not in priority_to_resolution:
        return False
    try:
        datetime.fromisoformat(ticket["created_time"])
    except ValueError:
        return False
    return True

def check_tickets():
    current_time = datetime.now()
    for ticket in tickets:
        if not validate_ticket(ticket):
            logging.error(f"Invalid ticket data: {ticket}")
            continue

        created_time = datetime.fromisoformat(ticket['created_time'])
        priority = ticket['priority']
        resolution_time = priority_to_resolution[priority]
        deadline = created_time + resolution_time
        time_left = deadline - current_time

        if time_left <= timedelta(hours=1):
            if priority in ["high", "critical"]:
                send_email_reminder(ticket, time_left)
                schedule_reminder(ticket, time_left, interval=15)
        elif time_left <= timedelta(hours=4):
            if priority in ["low", "medium"]:
                send_email_reminder(ticket, time_left)
                schedule_reminder(ticket, time_left, interval=60)

def send_email_reminder(ticket, time_left):
    body = (f"Dear Support Team,\n\n"
            f"This is a reminder that the following ticket needs your attention:\n\n"
            f"Ticket ID: {ticket['id']}\n"
            f"Priority: {ticket['priority'].capitalize()}\n"
            f"Time left to resolve: {str(time_left)}\n\n"
            f"Please ensure that the issue is resolved within the allocated time.\n\n"
            f"Thank you.\n"
            f"Support Team")
    send_email(EMAIL_TO, EMAIL_SUBJECT, body)

def schedule_reminder(ticket, time_left, interval):
    def reminder_job():
        send_email_reminder(ticket, time_left)
    schedule.every(interval).minutes.do(reminder_job)

# Schedule the ticket checking job
schedule.every(15).minutes.do(check_tickets)

# Start the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
