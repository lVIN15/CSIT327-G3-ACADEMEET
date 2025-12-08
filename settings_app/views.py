from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import get_user_model, update_session_auth_hash

# IMPORTANT: Ensure Schedule is imported from your core app
from core.models import Schedule 
from .models import UserProfile, TeacherAvailability, SystemHoliday
from .forms import CustomPasswordChangeForm, NotificationUpdateForm

import json
from datetime import datetime

User = get_user_model()

# --- Helper Functions (Permission Checks) ---

def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return user.userprofile.role == 'ADMIN'
    except UserProfile.DoesNotExist:
        return False

# ----------------------------------------------------------------------
# 1. GENERAL SETTINGS VIEW (ADMIN ACCESS ONLY)
# ----------------------------------------------------------------------

@user_passes_test(is_admin, login_url='admin_dashboard')
def general_settings(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.email = request.POST.get('email', request.user.email)
            request.user.save()

            if 'profile_picture' in request.FILES:
                user_profile.profile_picture = request.FILES['profile_picture']
            
            user_profile.save()
            messages.success(request, "Account information updated successfully.")
            
        elif action == 'change_role':
            target_user_id = request.POST.get('target_user_id')
            new_role = request.POST.get('new_role')
            try:
                target_user = User.objects.get(id=target_user_id)
                target_profile = UserProfile.objects.get(user=target_user)
                target_profile.role = new_role
                target_profile.save()
                messages.success(request, f"Role for {target_user.username} changed to {new_role}.")
            except (User.DoesNotExist, UserProfile.DoesNotExist):
                messages.error(request, "Error: Target user not found.")
            
        elif action == 'change_password':
            messages.info(request, "Password change feature is pending form integration.")
            
        return redirect('general_settings')
        
    context = {
        'user_profile': user_profile,
        'is_admin_user': True,
        'all_users': User.objects.all().select_related('userprofile').exclude(id=request.user.id),
    }
    return render(request, 'general.html', context)


from datetime import time # Make sure this is imported at the top

# ----------------------------------------------------------------------
# 2. ADMIN SETTINGS VIEW (CALENDAR & USER LISTS)
# ----------------------------------------------------------------------

@user_passes_test(is_admin, login_url='admin_dashboard')
def admin_settings(request: HttpRequest) -> HttpResponse:
    """
    Modified to display Professor Schedule Calendar in 12-HOUR FORMAT.
    """
    teachers = UserProfile.objects.filter(role='TEACHER').select_related('user').order_by('user__first_name')
    students = UserProfile.objects.filter(role='STUDENT').select_related('user').order_by('user__first_name')
    
    # Generate time slots in 12-Hour format (07:00 AM to 08:30 PM)
    time_slots = []
    for hour in range(7, 21): # 7 AM to 8 PM
        # Create time objects and format them to "07:00 AM", "01:30 PM" etc.
        t1 = time(hour, 0)
        t2 = time(hour, 30)
        time_slots.append(t1.strftime("%I:%M %p"))
        time_slots.append(t2.strftime("%I:%M %p"))
    
    context = {
        'teachers': teachers,
        'students': students,
        'is_admin_user': True,
        'time_slots': time_slots,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    }
    return render(request, 'admin_settings.html', context)


# ----------------------------------------------------------------------
# 2.1 API: FETCH PROFESSOR SCHEDULE (For Admin Calendar)
# ----------------------------------------------------------------------

@user_passes_test(is_admin, login_url='admin_dashboard')
def get_professor_schedule_admin(request):
    """
    AJAX Endpoint to fetch a specific professor's schedule.
    UPDATED: Returns 12-hour format to match the HTML grid.
    """
    professor_id = request.GET.get('professor_id')
    
    if not professor_id:
        return JsonResponse({'error': 'No professor ID provided'}, status=400)

    try:
        # Fetch schedules for the specific professor
        schedules = Schedule.objects.filter(professor_id=professor_id)
        
        data = []
        for sched in schedules:
            data.append({
                'id': sched.id,
                'day': sched.day,
                # CRITICAL: This must format exactly like the time_slots above ("%I:%M %p")
                # Example: "01:00 PM" instead of "13:00"
                'start_time': sched.start_time.strftime("%I:%M %p"), 
                'end_time': sched.end_time.strftime("%I:%M %p"),
                
                'subject_code': sched.subject_code,
                'room': sched.room,
                'status': sched.status,
                'display_start': sched.start_time.strftime("%I:%M %p"),
                'display_end': sched.end_time.strftime("%I:%M %p"),
            })
            
        return JsonResponse({'schedules': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ----------------------------------------------------------------------
# 3. OTHER SETTINGS VIEWS
# ----------------------------------------------------------------------

@user_passes_test(is_admin, login_url='admin_dashboard')
def teacher_settings(request):
    all_teachers = UserProfile.objects.filter(role='TEACHER').select_related('user')
    if request.method == 'POST':
        messages.info(request, "Teacher management features are pending implementation.")
        return redirect('teacher_settings')

    schedules = TeacherAvailability.objects.filter(teacher_profile__in=all_teachers).order_by('teacher_profile__user__username', 'day_of_week', 'start_time')
    context = {
        'all_teachers': all_teachers,
        'schedules': schedules,
        'is_admin_user': True,
    }
    return render(request, 'teacher_settings.html', context)

@user_passes_test(is_admin, login_url='admin_dashboard')
def student_settings(request):
    if request.method == 'POST' and request.POST.get('action') == 'update_student_defaults':
        messages.success(request, "Student default settings updated successfully.")
        return redirect('student_settings')
    teachers = UserProfile.objects.filter(role='TEACHER').select_related('user')
    context = {
        'teachers': teachers,
        'is_admin_user': True,
    }
    return render(request, 'student_settings.html', context)

@user_passes_test(is_admin, login_url='admin_dashboard')
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = request.POST.get('first_name', '')
            user.save()
            UserProfile.objects.create(user=user, role=role)
            messages.success(request, f"User '{username}' ({role}) created successfully.")
        except IntegrityError:
            messages.error(request, "User creation failed: Username or Email already exists.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            
    return redirect('admin_settings')

@user_passes_test(is_admin, login_url='admin_dashboard')
def edit_user(request, user_id):
    messages.info(request, f"User Edit feature for ID {user_id} is currently under construction.")
    return redirect('admin_settings')

@login_required
def view_user_profile(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    try:
        user_profile_data = target_user.userprofile
    except UserProfile.DoesNotExist:
        user_profile_data = None
    
    context = {
        'target_user': target_user,
        'user_profile': user_profile_data 
    }
    return render(request, 'user_profile.html', context)

@login_required(login_url='/login/')
def settings_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    is_professor = False
    is_student = False
        
    if profile and profile.role == 'STUDENT': 
        is_student = True   
    if profile and profile.role == 'TEACHER':
        is_professor = True
    
    if is_professor:
        template_name = 'settings.html'
        dashboard_url_name = 'professor_dashboard'
    else:
        template_name = 'student_settings.html'
        dashboard_url_name = 'student_dashboard'

    active_tab = request.GET.get('tab', 'account')
    
    password_form = CustomPasswordChangeForm(user=user)
    notification_form = NotificationUpdateForm(
        initial={
            'email_notifications': profile.email_notifications,
            'in_app_notifications': profile.in_app_notifications
        }
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_password':
            password_form = CustomPasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) 
                messages.success(request, 'Your password was successfully updated!')
                return redirect(f"{request.path}?tab=password")
            else:
                active_tab = 'password'
                
        elif action == 'update_preferences':
            notification_form = NotificationUpdateForm(request.POST, instance=profile)
            if notification_form.is_valid():
                notification_form.save()
                messages.success(request, 'Notification settings saved successfully.')
                return redirect(f"{request.path}?tab=account")
            else:
                active_tab = 'account'

    context = {
        'user_profile': profile,
        'user': user,
        'password_form': password_form,
        'notification_form': notification_form,
        'active_tab': active_tab,
        'dashboard_url_name': dashboard_url_name, 
    }
    return render(request, template_name, context)

# settings_app/views.py

from django.views.decorators.http import require_POST
import json

# ... existing imports and views ...

# --- NEW: API TO DELETE SCHEDULE ---
@require_POST
@user_passes_test(is_admin, login_url='admin_dashboard')
def delete_schedule_api(request):
    try:
        data = json.loads(request.body)
        schedule_id = data.get('schedule_id')
        
        if not schedule_id:
            return JsonResponse({'success': False, 'error': 'No ID provided'})

        # Find and delete
        schedule = Schedule.objects.get(id=schedule_id)
        schedule.delete()
        
        return JsonResponse({'success': True})
    except Schedule.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Schedule not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})