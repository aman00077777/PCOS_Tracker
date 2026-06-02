from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.models.user import User
from app.routers.auth import get_current_user
from app.services.alerts import send_discord_alert, send_email_alert

router = APIRouter(prefix="/alerts", tags=["Reminders & Alerts"])

class MedicationReminder(BaseModel):
    medication_name: str
    dosage: str
    time: str  # e.g. "08:00 AM" or "Night before bed"
    notes: Optional[str] = None
    email_recipient: Optional[EmailStr] = None

class AppointmentReminder(BaseModel):
    doctor_name: str
    clinic_name: str
    appointment_time: str  # DateTime string or text
    notes: Optional[str] = None
    email_recipient: Optional[EmailStr] = None

@router.post("/medication")
async def trigger_medication_reminder(
    reminder: MedicationReminder,
    current_user: User = Depends(get_current_user)
):
    """
    Triggers a medication reminder to Discord and/or Email.
    """
    message = (
        f"[PCOS Tracker Medication Reminder]\n"
        f"Hello {current_user.full_name or 'User'},\n"
        f"This is a reminder to take your medication:\n"
        f"- Name: {reminder.medication_name}\n"
        f"- Dosage: {reminder.dosage}\n"
        f"- Scheduled Time: {reminder.time}\n"
    )
    if reminder.notes:
        message += f"- Notes: {reminder.notes}\n"

    discord_ok = await send_discord_alert(message)
    
    email_ok = False
    recipient = reminder.email_recipient or current_user.email
    if recipient:
        subject = f"PCOS Tracker Medication Reminder: {reminder.medication_name}"
        email_ok = send_email_alert(
            recipient=recipient,
            subject=subject,
            body=message
        )
        
    return {
        "status": "Notification request processed",
        "discord_sent": discord_ok,
        "email_sent": email_ok,
        "recipient": recipient
    }

@router.post("/appointment")
async def trigger_appointment_reminder(
    reminder: AppointmentReminder,
    current_user: User = Depends(get_current_user)
):
    """
    Triggers an appointment reminder to Discord and/or Email.
    """
    message = (
        f"[PCOS Tracker Appointment Reminder]\n"
        f"Hello {current_user.full_name or 'User'},\n"
        f"You have an upcoming medical appointment scheduled:\n"
        f"- Doctor: {reminder.doctor_name}\n"
        f"- Clinic: {reminder.clinic_name}\n"
        f"- Time: {reminder.appointment_time}\n"
    )
    if reminder.notes:
        message += f"- Notes: {reminder.notes}\n"

    discord_ok = await send_discord_alert(message)
    
    email_ok = False
    recipient = reminder.email_recipient or current_user.email
    if recipient:
        subject = f"PCOS Tracker Appointment: Dr. {reminder.doctor_name}"
        email_ok = send_email_alert(
            recipient=recipient,
            subject=subject,
            body=message
        )
        
    return {
        "status": "Notification request processed",
        "discord_sent": discord_ok,
        "email_sent": email_ok,
        "recipient": recipient
    }

@router.post("/test-discord")
async def test_discord_webhook(current_user: User = Depends(get_current_user)):
    """
    Send a direct test alert to confirm Discord webhook is operational.
    """
    msg = f"[PCOS Tracker Webhook Test]\nHello {current_user.full_name or 'User'}! Your Discord integration is working."
    success = await send_discord_alert(msg)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send notification. Please check if settings.DISCORD_WEBHOOK_URL is set correctly."
        )
    return {"message": "Test alert dispatched successfully."}
