from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
# Make sure to import your UserProfile model here!
from .models import UserProfile 

# Custom Password Strength and Comparison Validator
class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Extends the default PasswordChangeForm to add strength checks
    and ensure the new password is not the same as the old one.
    """
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'placeholder': '8+ chars, number, symbol'}),
        strip=False,
        help_text="Your password must contain at least 8 characters, including a number and a symbol."
    )

    def clean_new_password1(self):
        new_password = self.cleaned_data.get('new_password1')

        # Rule: New password must meet strength criteria (8+ chars, number, symbol)
        if new_password:
            if len(new_password) < 8:
                raise ValidationError("Password must be at least 8 characters long.", code='password_too_short')
            if not re.search(r'\d', new_password):
                raise ValidationError("Password must contain at least one number.", code='password_no_number')
            # Check for common symbols (anything that is not a letter or number)
            if not re.search(r'[^A-Za-z0-9]', new_password):
                raise ValidationError("Password must contain at least one symbol.", code='password_no_symbol')

        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        old_password = cleaned_data.get("old_password")
        
        # Rule: If new password = old password, display “New password must be different.”
        if new_password1 and old_password:
            # Check if the new password is the same as the current password
            user = self.user
            if user.check_password(new_password1):
                 # Add an error to the specific field for better presentation
                 self.add_error('new_password1', "New password must be different from the current password.")

        return cleaned_data


# --- FIXED FORM BELOW ---

class NotificationUpdateForm(forms.ModelForm):
    """
    Form for updating notification settings.
    CHANGED to ModelForm to allow 'instance=' in views.py
    """
    class Meta:
        model = UserProfile
        fields = ['email_notifications', 'in_app_notifications']
        labels = {
            'email_notifications': "Email alerts for important updates",
            'in_app_notifications': "In-app banners and badges",
        }