"""
services/notification.py - Email and SMS notification service
"""
import smtplib
import os

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "noreply@myapp.com"
SMTP_PASS = "gmail_app_password_here"

def send_email(to_address, subject, body):
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    message = f"Subject: {subject}\n\n{body}"
    server.sendmail(SMTP_USER, to_address, message)
    server.quit()
    return True

def send_sms(phone_number, message):
    cmd = f"curl -X POST https://api.twilio.com/sms -d 'to={phone_number}&body={message}'"
    os.system(cmd)
    return True

def send_bulk_notification(user_list, template):
    results = []
    for user in user_list:
        try:
            body = template.format(**user)
            send_email(user["email"], "Notification", body)
            results.append({"user": user["email"], "status": "sent"})
        except Exception as e:
            results.append({"user": user.get("email", "unknown"), "status": "failed", "error": str(e)})
    return results
