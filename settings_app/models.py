# settings_app/models.py
from django.db import models
from django.contrib.auth.models import User

# --- 1. User Profile Extension ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    ]
    
    
    #NEW - NOV.18
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    subjects_notes = models.TextField(null=True, blank=True)
    profile_visible = models.BooleanField(default=True) 

    #def __str__(self):
        #return self.user.username + " Profile"



    #NEW - NOV.18
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    

    #new - nov19
    from django.db.models.signals import post_save
    from django.dispatch import receiver
    
    # NEW FIELD: This field is now correctly defined in the model
    is_professor = models.BooleanField(default=False)
    
    email_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    # Signal to ensure a UserProfile is created whenever a new User is created
    @receiver(post_save, sender=User)
    def create_or_update_user_profile(sender, instance, created, **kwargs):
     if created:
        UserProfile.objects.create(user=instance)
        try:
            instance.userprofile.save()
        except UserProfile.DoesNotExist:
        # If a user is saved without an existing profile (shouldn't happen with the `created` check)
            pass
    



# --- 2. Teacher Availability ---
class TeacherAvailability(models.Model):
    teacher_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BUSY', 'Busy'),
        ('ON_LEAVE', 'On Leave'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AVAILABLE')
    
    # Required for views.py
    DAY_OF_WEEK_CHOICES = (
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), 
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    )
    
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES) 
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        verbose_name = "Teacher Availability Slot"
        verbose_name_plural = "Teacher Availability Slots"
    
    def __str__(self):
        return f"{self.teacher_profile.user.username}'s Schedule on Day {self.day_of_week}"


# --- 3. Holiday / No-Class Day Settings ---
class SystemHoliday(models.Model):
    """
    Model to store non-working days for the system.
    The date field is unique.
    """
    CATEGORY_CHOICES = [
        ('FEDERAL', 'Federal Holiday'),
        ('SCHOOL', 'School Break'),
        ('OTHER', 'Other Holiday'),
    ]

    date = models.DateField(unique=True, verbose_name="Holiday Date")
    name = models.CharField(max_length=100, verbose_name="Holiday Name")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER', verbose_name="Category")

    class Meta:
        verbose_name = "System Holiday"
        verbose_name_plural = "System Holidays"
        ordering = ['date']

    def __str__(self):
        return f"{self.name} on {self.date}"