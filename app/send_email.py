import pyotp, random
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from . models import *

def send_otp(request, user_email):


    # Generate a random 4-digit OTP
    otp = str(random.randint(1000, 9999))


    # Get the current time
    now = timezone.now()

    # Set the expiry time (e.g., 5 minutes from the current time)
    expiry_time = now + timedelta(minutes=1)

    # Format the expiry_time as a human-readable string
    expiry_time_str = expiry_time.strftime("%B %d, %Y %I:%M %p")

    scheme = request.scheme  # http or https
    host = request.META['HTTP_HOST']  # This gives you the host, e.g., "127.0.0.1:8000"

    # Send the OTP to the user via email
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp}\n Click Here to verify your otp link ----->  {scheme}://{host}/verify_otp/api'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    # store it into db
    user = custom_usermodel.objects.get(email=user_email)

    try:
        otp_record = OTP.objects.get(author=user)
        # Update the existing OTP record
        otp_record.OTP_digit = otp
        otp_record.expiry_time = expiry_time
        otp_record.save()
    except OTP.DoesNotExist:
        # Create a new OTP record if it doesn't exist
        otp_record = OTP(author=user, OTP_digit=otp, expiry_time=expiry_time)
        otp_record.save()


    response = {
        "status" : status.HTTP_200_OK,
        'expiry_time': expiry_time_str,
        "message": "OTP sent successfully"

    }

    return response
