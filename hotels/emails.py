from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Booking
import logging

logger = logging.getLogger(__name__)


def send_booking_confirmation_email(booking):
    """Send booking confirmation email to the customer"""
    try:
        subject = f'Booking Confirmation - {booking.booking_id}'
        
        # Render HTML email template
        html_content = render_to_string('emails/booking_confirmation.html', {
            'booking': booking,
            'user': booking.user,
            'hotel': booking.hotel,
            'site_name': getattr(settings, 'SITE_NAME', 'BookingMVP'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@bookingmvp.com'),
        })
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f'Booking confirmation email sent to {booking.user.email} for booking {booking.booking_id}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send booking confirmation email: {str(e)}')
        return False


def send_booking_cancellation_email(booking):
    """Send booking cancellation email to the customer"""
    try:
        subject = f'Booking Cancellation - {booking.booking_id}'
        
        # Render HTML email template
        html_content = render_to_string('emails/booking_cancellation.html', {
            'booking': booking,
            'user': booking.user,
            'hotel': booking.hotel,
            'site_name': getattr(settings, 'SITE_NAME', 'BookingMVP'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@bookingmvp.com'),
        })
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f'Booking cancellation email sent to {booking.user.email} for booking {booking.booking_id}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send booking cancellation email: {str(e)}')
        return False


def send_hotel_owner_notification(booking, action='new_booking'):
    """Send notification to hotel owner about booking activities"""
    try:
        # Get hotel owner email (you might need to adjust this based on your user model)
        hotel_owner_email = getattr(booking.hotel, 'owner_email', 'owner@hotel.com')
        
        if action == 'new_booking':
            subject = f'New Booking Received - {booking.booking_id}'
            template = 'emails/hotel_owner_new_booking.html'
        elif action == 'booking_cancelled':
            subject = f'Booking Cancelled - {booking.booking_id}'
            template = 'emails/hotel_owner_booking_cancelled.html'
        else:
            return False
        
        # Render HTML email template
        html_content = render_to_string(template, {
            'booking': booking,
            'user': booking.user,
            'hotel': booking.hotel,
            'site_name': getattr(settings, 'SITE_NAME', 'BookingMVP'),
            'admin_url': f'{settings.BASE_URL}/admin/',
        })
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[hotel_owner_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f'Hotel owner notification sent to {hotel_owner_email} for booking {booking.booking_id}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send hotel owner notification: {str(e)}')
        return False


def send_reminder_email(booking, reminder_type='check_in'):
    """Send reminder emails to customers"""
    try:
        if reminder_type == 'check_in':
            subject = f'Check-in Reminder - {booking.hotel.name}'
            template = 'emails/check_in_reminder.html'
        elif reminder_type == 'check_out':
            subject = f'Check-out Reminder - {booking.hotel.name}'
            template = 'emails/check_out_reminder.html'
        else:
            return False
        
        # Render HTML email template
        html_content = render_to_string(template, {
            'booking': booking,
            'user': booking.user,
            'hotel': booking.hotel,
            'site_name': getattr(settings, 'SITE_NAME', 'BookingMVP'),
        })
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f'{reminder_type.title()} reminder email sent to {booking.user.email} for booking {booking.booking_id}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send {reminder_type} reminder email: {str(e)}')
        return False


def send_welcome_email(user):
    """Send welcome email to new users"""
    try:
        subject = f'Welcome to {getattr(settings, "SITE_NAME", "BookingMVP")}!'
        
        # Render HTML email template
        html_content = render_to_string('emails/welcome.html', {
            'user': user,
            'site_name': getattr(settings, 'SITE_NAME', 'BookingMVP'),
            'site_url': getattr(settings, 'BASE_URL', 'http://localhost:8000'),
        })
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f'Welcome email sent to {user.email}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send welcome email: {str(e)}')
        return False