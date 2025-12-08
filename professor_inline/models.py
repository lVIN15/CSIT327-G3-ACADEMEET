# In your models.py
from django.db import models
from django.contrib.auth.models import User

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True) # Usually linked to user.email
    profile_picture = models.ImageField(upload_to='professor_pics/', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    office_location = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True) # New field

    def __str__(self):
        return f"Profile for {self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()