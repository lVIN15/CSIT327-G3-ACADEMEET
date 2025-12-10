#!/usr/bin/env python
"""
Test script to verify Brevo API email sending works correctly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academeet.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 60)
print("BREVO API EMAIL TEST")
print("=" * 60)

# Check configuration
print("\n1. Checking Brevo configuration:")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   BREVO_API_KEY: {settings.ANYMAIL.get('BREVO_API_KEY', 'NOT SET')}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Test sending email
print("\n2. Attempting to send test email via Brevo API...")
try:
    result = send_mail(
        subject='Academeet Brevo API Test',
        message='If you received this email, Brevo API is working correctly!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['academeet.25@gmail.com'],
        fail_silently=False
    )
    print(f"   ✅ Email sent successfully! (returned: {result})")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
