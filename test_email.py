#!/usr/bin/env python
"""
Test script to verify email configuration is working correctly.
Run this before testing the forgot password feature.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academeet.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 60)
print("EMAIL CONFIGURATION TEST")
print("=" * 60)

# Check environment variables
print("\n1. Checking environment variables:")
print(f"   EMAIL_HOST_USER: {os.environ.get('EMAIL_HOST_USER', 'NOT SET')}")
print(f"   EMAIL_HOST_PASSWORD: {'***HIDDEN***' if os.environ.get('EMAIL_HOST_PASSWORD') else 'NOT SET'}")
print(f"   EMAIL_BACKEND: {os.environ.get('EMAIL_BACKEND', 'NOT SET')}")

# Check Django settings
print("\n2. Checking Django settings:")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Try to send a test email
print("\n3. Attempting to send test email...")
try:
    from_email = os.environ.get('EMAIL_HOST_USER', settings.DEFAULT_FROM_EMAIL)
    
    if not from_email or from_email == 'noreply@academeet.local':
        print("   ❌ ERROR: EMAIL_HOST_USER is not set!")
        print("   Set it before running the server:")
        print("   $env:EMAIL_HOST_USER = 'academeet.25@gmail.com'")
        print("   $env:EMAIL_HOST_PASSWORD = 'your-app-password'")
        exit(1)
    
    send_mail(
        subject='Academeet Email Test',
        message='This is a test email from Academeet. If you received this, email is configured correctly!',
        from_email=from_email,
        recipient_list=[from_email],  # Send to self for testing
        fail_silently=False
    )
    print(f"   ✅ SUCCESS! Email sent from {from_email}")
    print("   Check your inbox to confirm delivery.")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    print(f"\n   Common issues:")
    print(f"   - Gmail app password is incorrect (spaces are removed automatically)")
    print(f"   - 2-Step Verification not enabled on Gmail account")
    print(f"   - App password not created at https://myaccount.google.com/apppasswords")
    exit(1)

print("\n" + "=" * 60)
print("If you see this message, email is working!")
print("=" * 60)
