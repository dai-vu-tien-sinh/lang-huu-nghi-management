import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import streamlit as st

def send_email(to_email: str, subject: str, content: str) -> bool:
    """
    Send an email using SendGrid API.
    Returns True if email was sent successfully, False otherwise.
    """
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        message = Mail(
            from_email="langhunghi@example.com",  # Replace with your verified sender
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def send_medical_notification(patient_email: str, appointment_date: str, doctor_name: str):
    """Send medical appointment notification."""
    subject = "Medical Appointment Reminder - Làng Hữu Nghị"
    content = f"""
    <h2>Medical Appointment Reminder</h2>
    <p>Dear patient,</p>
    <p>This is a reminder for your upcoming medical appointment:</p>
    <ul>
        <li>Date: {appointment_date}</li>
        <li>Doctor: {doctor_name}</li>
    </ul>
    <p>Location: Làng Hữu Nghị Medical Center</p>
    """
    return send_email(patient_email, subject, content)

def send_psychological_notification(student_email: str, evaluation_date: str, counselor_name: str):
    """Send psychological evaluation notification."""
    subject = "Psychological Evaluation Appointment - Làng Hữu Nghị"
    content = f"""
    <h2>Psychological Evaluation Appointment</h2>
    <p>Dear student,</p>
    <p>Your psychological evaluation has been scheduled:</p>
    <ul>
        <li>Date: {evaluation_date}</li>
        <li>Counselor: {counselor_name}</li>
    </ul>
    <p>Location: Làng Hữu Nghị Counseling Center</p>
    """
    return send_email(student_email, subject, content)

def send_admin_notification(admin_email: str, subject: str, message: str):
    """Send administrative notification."""
    content = f"""
    <h2>Administrative Notification - Làng Hữu Nghị</h2>
    <p>{message}</p>
    """
    return send_email(admin_email, subject, content)
