from flask import current_app
from flask_mail import Message
from twilio.rest import Client
from app import mail

class NotificationManager:
    @staticmethod
    def send_email(to, subject, template):
        """
        Send email notification
        """
        try:
            msg = Message(
                subject,
                recipients=[to],
                html=template,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Email sending failed: {str(e)}")
            return False

    @staticmethod
    def send_sms(to, message):
        """
        Send SMS notification using Twilio
        """
        try:
            client = Client(
                current_app.config['TWILIO_ACCOUNT_SID'],
                current_app.config['TWILIO_AUTH_TOKEN']
            )
            
            message = client.messages.create(
                body=message,
                from_=current_app.config['TWILIO_PHONE_NUMBER'],
                to=to
            )
            return True
        except Exception as e:
            current_app.logger.error(f"SMS sending failed: {str(e)}")
            return False

    @classmethod
    def send_result_notification(cls, student, result_type):
        """
        Send result publication notification
        """
        # Email notification
        email_template = f"""
        <h2>Result Published</h2>
        <p>Dear {student.name},</p>
        <p>Your {result_type} results have been published. Please log in to your student portal to view them.</p>
        <p>Best regards,<br>School Administration</p>
        """
        cls.send_email(
            student.email,
            f"{result_type} Results Published",
            email_template
        )

        # SMS notification
        sms_message = f"Dear {student.name}, your {result_type} results have been published. Please check your student portal."
        if student.phone:
            cls.send_sms(student.phone, sms_message)

    @classmethod
    def send_fee_reminder(cls, student, fee_details):
        """
        Send fee payment reminder
        """
        # Email notification
        email_template = f"""
        <h2>Fee Payment Reminder</h2>
        <p>Dear {student.name},</p>
        <p>This is a reminder that your fee payment of {fee_details['amount']} is due on {fee_details['due_date']}.</p>
        <p>Fee Details:</p>
        <ul>
            <li>Amount: {fee_details['amount']}</li>
            <li>Due Date: {fee_details['due_date']}</li>
            <li>Fee Type: {fee_details['fee_type']}</li>
        </ul>
        <p>Please make the payment before the due date to avoid any late fees.</p>
        <p>Best regards,<br>School Administration</p>
        """
        cls.send_email(
            student.email,
            "Fee Payment Reminder",
            email_template
        )

        # SMS notification
        sms_message = f"Dear {student.name}, your fee payment of {fee_details['amount']} is due on {fee_details['due_date']}. Please pay before the due date."
        if student.phone:
            cls.send_sms(student.phone, sms_message) 