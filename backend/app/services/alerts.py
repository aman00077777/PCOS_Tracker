import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from app.config import settings

async def send_discord_alert(content: str) -> bool:
    """
    Sends an alert notification via Discord webhook.
    """
    if not settings.DISCORD_WEBHOOK_URL:
        print("[DISCORD ALERT SKIP] Webhook URL not configured.")
        return False

    try:
        async with httpx.AsyncClient() as client:
            payload = {"content": content}
            response = await client.post(settings.DISCORD_WEBHOOK_URL, json=payload)
            if response.status_code in [200, 204]:
                print("[DISCORD ALERT SUCCESS] Notification sent.")
                return True
            else:
                print(f"[DISCORD ALERT ERROR] Failed to send. Status: {response.status_code}")
                return False
    except Exception as e:
        print(f"[DISCORD ALERT ERROR] Exception: {str(e)}")
        return False

def send_email_alert(recipient: str, subject: str, body: str) -> bool:
    """
    Sends a medication or appointment reminder alert via SMTP.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("[EMAIL ALERT SKIP] SMTP credentials not fully configured.")
        return False

    try:
        # Create message container
        msg = MIMEMultipart()
        msg["From"] = settings.MAIL_FROM
        msg["To"] = recipient
        msg["Subject"] = subject

        # Attach text body
        msg.attach(MIMEText(body, "plain"))

        # Setup SMTP server
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        # Send mail
        server.sendmail(settings.MAIL_FROM, recipient, msg.as_string())
        server.quit()
        
        print(f"[EMAIL ALERT SUCCESS] Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"[EMAIL ALERT ERROR] Exception: {str(e)}")
        return False
