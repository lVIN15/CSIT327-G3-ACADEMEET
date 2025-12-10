from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import get_messages
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import Schedule, Holiday
from datetime import datetime, timedelta
import random
import os
from academeet.supabase_client import get_holidays

User = get_user_model()

def home(request):
    return render(request, 'role_selection.html')


# -------------------- SIGNUP VIEWS --------------------

def student_signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Collect additional information but don't require it for account creation
        student_id = request.POST.get('student_id')
        contact_number = request.POST.get('contact_number')
        course = request.POST.get('course')
        year_level = request.POST.get('year_level')

        if not all([full_name, email, password1, password2]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'student_signup.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'student_signup.html')

        if User.objects.filter(username=email).exists():
            messages.warning(request, 'An account with that email already exists. Please login.')
            return redirect('student_login')

        # Create user account with basic information
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=full_name
        )
        messages.success(request, 'Student account created successfully. Please log in.')
        return redirect('student_login')

    return render(request, 'student_signup.html')


def teacher_signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Get additional fields but don't require them yet
        teacher_id = request.POST.get('teacher_id')
        contact_number = request.POST.get('contact_number')
        department = request.POST.get('department')

        if not all([full_name, email, password1, password2]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'teacher_signup.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'teacher_signup.html')

        if User.objects.filter(username=email).exists():
            messages.warning(request, 'An account with that email already exists. Please login.')
            return redirect('teacher_login')

        try:
            # Create basic user account
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=full_name
            )
            messages.success(request, 'Teacher account created successfully. Please log in.')
            return redirect('teacher_login')
        except Exception as e:
            messages.error(request, 'Error creating account. Please try again.')
            return render(request, 'teacher_signup.html')

    return render(request, 'teacher_signup.html')


# -------------------- LOGIN VIEWS --------------------

def student_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('student_dashboard')
        if not User.objects.filter(username=email).exists():
            return render(request, 'student_login.html', {'error': 'Email not registered. Please sign up.'})
        else:
            return render(request, 'student_login.html', {'error': 'Incorrect password. Please try again.'})
    return render(request, 'student_login.html')


def teacher_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Welcome back! Redirecting to professor dashboard.')
            return redirect('professor_dashboard')
        if not User.objects.filter(username=email).exists():
            return render(request, 'teacher_login.html', {'error': 'Email not registered. Please sign up.'})
        else:
            return render(request, 'teacher_login.html', {'error': 'Incorrect password. Please try again.'})
    return render(request, 'teacher_login.html')



#------------------------NEW FOR ADMIN DASHBOARD----------------
def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_superuser:  # only superusers can enter admin_dashboard
                auth_login(request, user)
                messages.success(request, 'Welcome, Admin!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access denied. You are not an admin.')
                return render(request, 'admin_login.html')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
            return render(request, 'admin_login.html')

    return render(request, 'admin_login.html')


# -------------------- PASSWORD MANAGEMENT --------------------

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'forgot_password_page.html')

        # Verify user exists
        try:
            User.objects.get(username=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found for that email address.')
            return render(request, 'forgot_password_page.html')

        # Generate 6-digit code and store with 90-second cooldown
        code = '{:06d}'.format(random.randint(0, 999999))
        expires_at = (datetime.now() + timedelta(seconds=90)).timestamp()
        request.session['pw_reset_email'] = email
        request.session['pw_reset_code'] = code
        request.session['pw_reset_expires'] = expires_at
        request.session['pw_reset_confirmed'] = False
        request.session.modified = True  # Ensure session is saved
        
        print(f"[DEBUG] Generated code: '{code}' for {email}")
        print(f"[DEBUG] Session keys: {list(request.session.keys())}")

        # Send code via email
        subject = 'Your Academeet password reset code'
        message = f'Use the following 6-digit code to reset your Academeet password: {code}\nThis code expires in 90 seconds.'
        
        # Get the from_email from Django settings (configured via DEFAULT_FROM_EMAIL)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'academeet.25@gmail.com')
        
        try:
            if not from_email:
                messages.error(request, 'Email service not configured. Please contact support.')
                return render(request, 'forgot_password_page.html')
            
            print(f"[DEBUG] Sending email from: {from_email}")
            print(f"[DEBUG] Sending email to: {email}")
            print(f"[DEBUG] Email backend: {settings.EMAIL_BACKEND}")
            
            # Actually send the email
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[email],
                fail_silently=False
            )
            print(f"[DEBUG] Email sent successfully!")
            messages.success(request, 'A 6-digit code was sent to your email address.')
        except Exception as e:
            print(f"[DEBUG] Email error: {str(e)}")
            messages.error(request, f'Failed to send email: {str(e)}')
            return render(request, 'forgot_password_page.html')

        return redirect('forgot_password_sent')
    return render(request, 'forgot_password_page.html')


def forgot_password_sent(request):
    email = request.session.get('pw_reset_email')
    code = request.session.get('pw_reset_code')
    expires_at = request.session.get('pw_reset_expires')
    confirmed = request.session.get('pw_reset_confirmed', False)

    cooldown_remaining = 0
    if expires_at:
        remaining = int(max(0, int(expires_at) - int(datetime.now().timestamp())))
        cooldown_remaining = remaining

    # Handle POST actions: resend or verify
    if request.method == 'POST':
        # Resend request
        if request.POST.get('resend') is not None or request.POST.get('email'):
            # Check if cooldown is still active
            if cooldown_remaining > 0:
                messages.error(request, f'Please wait {cooldown_remaining} seconds before requesting a new code.')
                return render(request, 'forgot_password_sent.html', {'email': email, 'cooldown_remaining': cooldown_remaining, 'confirmed': confirmed, 'code': code})
            
            new_email = request.POST.get('email', email)
            if not new_email:
                messages.error(request, 'No email provided to resend to.')
            else:
                try:
                    User.objects.get(username=new_email)
                except User.DoesNotExist:
                    messages.error(request, 'No account found for that email address.')
                    return render(request, 'forgot_password_sent.html', {'email': email, 'cooldown_remaining': cooldown_remaining, 'confirmed': confirmed, 'code': code})

                # Regenerate code and reset cooldown
                code = '{:06d}'.format(random.randint(0, 999999))
                expires_at = (datetime.now() + timedelta(seconds=90)).timestamp()
                request.session['pw_reset_code'] = code
                request.session['pw_reset_expires'] = expires_at
                request.session['pw_reset_confirmed'] = False
                request.session['pw_reset_email'] = new_email
                request.session['pw_reset_code'] = code
                request.session['pw_reset_expires'] = expires_at
                request.session['pw_reset_confirmed'] = False
                request.session.modified = True  # Ensure session is saved
                cooldown_remaining = 90

                # Send email
                subject = 'Your Academeet password reset code'
                message = f'Use the following 6-digit code to reset your Academeet password: {code}\nThis code expires in 90 seconds.'
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'academeet.25@gmail.com')
                try:
                    if from_email:
                        send_mail(subject, message, from_email, [new_email], fail_silently=False)
                        print(f"[DEBUG] Resent code '{code}' to {new_email}")
                        messages.success(request, 'A new 6-digit code was sent to your email address.')
                    else:
                        messages.warning(request, 'Email not configured. Code regenerated for testing.')
                except Exception as e:
                    print(f"[DEBUG] Resend error: {str(e)}")
                    messages.error(request, f'Failed to send email: {str(e)}')

        # Verify provided confirmation code
        if request.POST.get('confirmation_code'):
            provided = request.POST.get('confirmation_code', '').strip()
            stored_code = request.session.get('pw_reset_code', '')
            
            print(f"\n[DEBUG] === CODE VERIFICATION ===")
            print(f"[DEBUG] Provided code: '{provided}' (type: {type(provided)}, len: {len(provided)})")
            print(f"[DEBUG] Stored code:   '{stored_code}' (type: {type(stored_code)}, len: {len(stored_code)})")
            print(f"[DEBUG] Match: {provided == stored_code}")
            print(f"[DEBUG] Session ID: {request.session.session_key}")
            print(f"[DEBUG] All session keys: {list(request.session.keys())}")
            print(f"[DEBUG] =====================\n")
            
            # Check expiry
            if not expires_at or datetime.now().timestamp() > float(expires_at):
                # AJAX requests get JSON response
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'The confirmation code has expired. Please resend.'})
                messages.error(request, 'The confirmation code has expired. Please resend.')
            elif provided == stored_code:
                request.session['pw_reset_confirmed'] = True
                request.session.modified = True
                print(f"[DEBUG] Code verified for {email}. Redirecting to reset_password.")
                # For AJAX return JSON with redirect url
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'redirect': reverse('reset_password')})
                # Include email in querystring to ensure reset view receives it even if session is flaky
                return redirect(reverse('reset_password') + f'?email={email}')
            else:
                # Debug: Log the mismatch
                error_msg = f'Invalid confirmation code. Please try again.'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': error_msg})
                messages.error(request, error_msg)

    return render(request, 'forgot_password_sent.html', {
        'email': email,
        'cooldown_remaining': cooldown_remaining,
        'confirmed': confirmed,
        'code': code,  # For debugging only
    })


def reset_password(request):
    email = request.GET.get('email') or request.session.get('pw_reset_email')
    confirmed = request.session.get('pw_reset_confirmed', False)
    
    # Require that the user has confirmed their code before resetting password
    if not confirmed:
        messages.error(request, 'Please verify your code first.')
        return redirect('forgot_password_sent')
    
    if request.method == 'POST':
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        if not new or new != confirm:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match.'})
        if not email:
            return render(request, 'reset_password.html', {'error': 'No email specified.'})
        try:
            user = User.objects.get(username=email)
            user.set_password(new)
            user.save()
            # Clear the password reset session variables
            request.session.pop('pw_reset_email', None)
            request.session.pop('pw_reset_code', None)
            request.session.pop('pw_reset_expires', None)
            request.session.pop('pw_reset_confirmed', None)
            return redirect('reset_password_success')
        except User.DoesNotExist:
            return render(request, 'reset_password.html', {'error': 'User not found.'})

    return render(request, 'reset_password.html')


def reset_password_success(request):
    return render(request, 'reset_password_success.html')


# -------------------- DASHBOARDS --------------------

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def student_dashboard(request):
    """
    Display student view of all professors' schedules.
    FIX: Removed .filter(status='Available') so students see everything (Classes, etc.)
    """
    # We remove the filter so ALL statuses (In Class, Available, Out of Work) are fetched
    schedules = Schedule.objects.select_related('professor').all().order_by(
        'day', 
        'start_time', 
        'professor__last_name' # Added ordering by name for cleaner list
    )
    
    context = {
        'schedules': schedules,
        'user_name': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'student_dashboard.html', context)





# ... existing imports ...
from django.shortcuts import render, redirect, get_object_or_404
# ... other imports ...

# 👇 ADD THIS IMPORT AT THE TOP OF THE FILE
from professor_inline.models import Professor 

# ...

@login_required(login_url='teacher_login')
def professor_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('teacher_login')
        
    schedules = Schedule.objects.filter(professor=request.user)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_time = datetime.strptime("07:00", "%H:%M")
    end_time = datetime.strptime("21:00", "%H:%M")
    delta = timedelta(minutes=30)
    
    # Get initial holidays for current month
    current_date = datetime.now()
    initial_holidays = get_holidays(current_date.year, current_date.month)
    
    # Build time slots (used for the grid rows)
    time_slots = []
    current_time = start_time
    while current_time <= end_time:
        label = current_time.strftime("%I:%M %p")
        time_slots.append((label, current_time.time()))
        current_time += delta

    grid_rows = []
    for label, t in time_slots:
        grid_rows.append({
            "label": label,
            "half_hour": (":30" in label),
            "bold_time": (":00" in label),
            "cells": [None for _ in days],
        })

    for sched in schedules:
        try:
            start = sched.start_time
            end = sched.end_time
            start_index = next(i for i, (_, t) in enumerate(time_slots) if t >= start)
            end_index = next(i for i, (_, t) in enumerate(time_slots) if t >= end)
        except StopIteration:
            continue

        rowspan = max(1, end_index - start_index)
        day_index = days.index(sched.day)

        grid_rows[start_index]["cells"][day_index] = {
            "subject_code": sched.subject_code,
            "subject_name": sched.subject_name,
            "section": sched.section,
            "room": sched.room,
            "status": sched.status,
            "rowspan": rowspan,
            "id": sched.id,
        }

        for i in range(start_index + 1, start_index + rowspan):
            if i < len(grid_rows):
                grid_rows[i]["cells"][day_index] = "SPAN"

    # --- NEW: Fetch Professor Profile Data for the Hover Card ---
    try:
        professor_profile = Professor.objects.get(user=request.user)
    except Professor.DoesNotExist:
        professor_profile = None
    # ------------------------------------------------------------

    context = {
        "grid_rows": grid_rows,
        "user_name": request.user.get_full_name() or request.user.username,
        "initial_holidays": initial_holidays,
        "professor_profile": professor_profile, # <-- Added to context
    }

    return render(request, "professor_dashboard.html", context)






#------------------------------NEW FOR ADMIN_DASHBOARD-----------------------

@login_required(login_url='admin_login')
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to access the admin dashboard.")
        return redirect('dashboard')  # send back to role selection

    context = {
        'user_name': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'admin_dashboard.html', context)

#----------------------------------------------------------------------------------



@login_required
def professor_schedule_view(request, professor_id):
    """
    Public view for students to see a specific professor's schedule.
    Shows the professor's weekly schedule in a read-only format.
    """
    professor = get_object_or_404(User, id=professor_id)
    schedules = Schedule.objects.filter(professor=professor)
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_time = datetime.strptime("07:00", "%H:%M")
    end_time = datetime.strptime("21:00", "%H:%M")
    delta = timedelta(minutes=30)

    time_slots = []
    current_time = start_time
    while current_time <= end_time:
        label = current_time.strftime("%I:%M %p")
        time_slots.append((label, current_time.time()))
        current_time += delta

    grid_rows = []
    for label, t in time_slots:
        grid_rows.append({
            "label": label,
            "half_hour": (":30" in label),
            "bold_time": (":00" in label),
            "cells": [None for _ in days],
        })

    for sched in schedules:
        try:
            start = sched.start_time
            end = sched.end_time
            start_index = next(i for i, (_, t) in enumerate(time_slots) if t >= start)
            end_index = next(i for i, (_, t) in enumerate(time_slots) if t >= end)
        except StopIteration:
            continue

        rowspan = max(1, end_index - start_index)
        day_index = days.index(sched.day)

        grid_rows[start_index]["cells"][day_index] = {
            "subject_code": sched.subject_code,
            "subject_name": sched.subject_name,
            "section": sched.section,
            "room": sched.room,
            "status": sched.status,
            "rowspan": rowspan,
            "id": sched.id,
        }

        for i in range(start_index + 1, start_index + rowspan):
            if i < len(grid_rows):
                grid_rows[i]["cells"][day_index] = "SPAN"

    context = {
        "grid_rows": grid_rows,
        "professor_name": professor.get_full_name() or professor.username,
        "user_name": request.user.get_full_name() or request.user.username,
    }

    return render(request, "professor_schedule_view.html", context)


# -------------------- SCHEDULE MANAGEMENT --------------------

@login_required
def add_schedule(request):
    if request.method == 'POST':
        subject_codes = request.POST.getlist('subject_code[]')
        subject_names = request.POST.getlist('subject_name[]')
        sections = request.POST.getlist('section[]')
        days = request.POST.getlist('day[]')
        start_times = request.POST.getlist('time_from[]')
        end_times = request.POST.getlist('time_to[]')
        statuses = request.POST.getlist('status[]')
        rooms = request.POST.getlist('room[]')
        year_levels = request.POST.getlist('year_level[]')
        departments = request.POST.getlist('department[]')

        for i in range(len(subject_codes)):
            Schedule.objects.create(
                professor=request.user,
                day=days[i],
                start_time=start_times[i],
                end_time=end_times[i],
                subject_code=subject_codes[i],
                subject_name=subject_names[i],
                section=sections[i],
                status=statuses[i],
                room=rooms[i],
                year_level=year_levels[i] if i < len(year_levels) else None,
                department=departments[i] if i < len(departments) else 'CCS'
            )

        messages.success(request, "Schedules successfully added.")
        return redirect('professor_dashboard')

    return render(request, 'add_schedule.html')


@login_required
def edit_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, professor=request.user)
    if request.method == 'POST':
        schedule.subject_code = request.POST.get('subject_code')
        schedule.subject_name = request.POST.get('subject_name')
        schedule.section = request.POST.get('section')
        schedule.room = request.POST.get('room')
        schedule.year_level = request.POST.get('year_level')
        schedule.day = request.POST.get('day')
        schedule.start_time = request.POST.get('time_from')
        schedule.end_time = request.POST.get('time_to')
        schedule.status = request.POST.get('status')
        schedule.department = request.POST.get('department', 'CCS')
        schedule.save()
        messages.success(request, "Schedule updated successfully.")
        return redirect('professor_dashboard')
    return render(request, 'edit_schedule.html', {'schedule': schedule})


@login_required
def delete_schedule(request, schedule_id):
    if request.method == 'POST':
        schedule = get_object_or_404(Schedule, id=schedule_id, professor=request.user)
        schedule.delete()
        messages.success(request, "Schedule deleted successfully.")
    return redirect('professor_dashboard')


# -------------------- LOGOUT --------------------

def logout_view(request):
    auth_logout(request)
    storage = get_messages(request)
    for _ in storage:
        pass
    return render(request, 'redirectingafterlogout_page.html')


# -------------------- API ENDPOINT FOR STUDENT DASHBOARD --------------------

@require_GET
@login_required
def get_schedules(request):
    professor_name = request.GET.get('professor', '')
    department = request.GET.get('department', '')
    timeslot = request.GET.get('timeslot', '')
    day = request.GET.get('day', '')

    schedules = Schedule.objects.all()

    if professor_name:
        schedules = schedules.filter(professor__first_name__icontains=professor_name)

    if department:
        schedules = schedules.filter(department=department)

    if day:
        schedules = schedules.filter(day=day)

    if timeslot:
        schedules = schedules.filter(start_time=timeslot)

    data = [{
        "id": s.id,
        "professor": s.professor.first_name,
        "department": s.get_department_display(),
        "day": s.day,
        "start_time": s.start_time.strftime('%I:%M %p'),
        "end_time": s.end_time.strftime('%I:%M %p'),
        "subject_code": s.subject_code,
        "subject_name": s.subject_name,
        "section": s.section,
        "room": s.room,
        "status": s.status,
    } for s in schedules]

    return JsonResponse({"schedules": data})