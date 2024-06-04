import json
import schedule
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

# Load tickets from a JSON file
with open('tickets.json') as f:
    tickets = json.load(f)

# Define deadline for each priority 
priority_to_resolution = {
    "low": timedelta(hours=8),
    "medium": timedelta(hours=6),
    "high": timedelta(hours=4),
    "critical": timedelta(hours=2)
}

# Email configuration
SMTP_SERVER = 'smpt.gmail.com'
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

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, [to], msg.as_string())

def check_tickets():
    current_time = datetime.now()
    for ticket in tickets:
        created_time = datetime.fromisoformat(ticket['created_time'])
        priority = ticket['priority']
        resolution_time = priority_to_resolution[priority]
        deadline = created_time + resolution_time
        time_left = deadline - current_time

        if time_left <= timedelta(hours=1):
            if priority in ["high", "critical"]:
                send_email_reminder(ticket, time_left)
                schedule_reminder(ticket, time_left, interval=15)
            elif priority in ["low", "medium"]:
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

# Schedule the ticket checking 
schedule.every(15).minutes.do(check_tickets)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)