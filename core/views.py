from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import get_messages
from django.views.decorators.http import require_GET
from django.db.models import Q
from .models import Schedule
from datetime import datetime, timedelta
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
        request.session['pw_reset_email'] = email
        return redirect('forgot_password_sent')
    return render(request, 'forgot_password_page.html')


def forgot_password_sent(request):
    email = request.session.get('pw_reset_email')
    cooldown_remaining = 0
    if request.method == 'POST':
        request.session['pw_reset_email'] = request.POST.get('email', email)
        cooldown_remaining = 90
    return render(request, 'forgot_password_sent.html', {'email': email, 'cooldown_remaining': cooldown_remaining})


def reset_password(request):
    email = request.GET.get('email') or request.session.get('pw_reset_email')
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