from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# CRITICAL CHANGE 1: Import UserProfile from the correct app (settings_app)
from settings_app.models import UserProfile 

User = get_user_model()

def is_admin(user):
    # Reusing the check to ensure the user is an admin/superuser
    return user.is_superuser

@login_required(login_url='admin_login')
def admin_dashboard(request):
    if not is_admin(request.user):
        messages.error(request, "You are not authorized to access this page.")
        return redirect('/')

    # Filtering
    role = request.GET.get('role')
    status = request.GET.get('status')

    # CRITICAL CHANGE 2: Use select_related to get the UserProfile data efficiently
    users = User.objects.all().select_related('userprofile').order_by('id') 

    # Handle Role Filtering based on UserProfile
    if role:
        # Assuming roles are 'ADMIN', 'TEACHER', 'STUDENT'
        if role.lower() == "admin":
             users = users.filter(userprofile__role='ADMIN')
        elif role.lower() == "teacher":
             users = users.filter(userprofile__role='TEACHER')
        elif role.lower() == "student":
             users = users.filter(userprofile__role='STUDENT')
    
    # Handle Status Filtering
    if status == "active":
        users = users.filter(is_active=True)
    elif status == "deactivated":
        users = users.filter(is_active=False)

    context = {
        'users': users,
        'user_name': request.user.get_full_name() or request.user.username,
        'current_role_filter': role, # Optional: to keep the filter button active
        'current_status_filter': status, # Optional: to keep the filter button active
    }
    return render(request, 'admin_dashboard.html', context)


@login_required(login_url='admin_login')
def toggle_user_status(request, user_id):
    if not is_admin(request.user):
        messages.error(request, "Unauthorized action.")
        return redirect('admin_dashboard')

    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()

    if user.is_active:
        messages.success(request, f"{user.email} has been activated.")
    else:
        messages.warning(request, f"{user.email} has been deactivated.")

    # Redirect back to the dashboard, preserving filters if possible
    redirect_url = request.META.get('HTTP_REFERER', 'admin_dashboard')
    return redirect(redirect_url)


from django.contrib.auth import authenticate, login, logout

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin.")
            return render(request, 'admin_login.html', {'error': "Invalid credentials or not an admin."})

    # CRITICAL FIX for the return statement (was rendering admin_dashboard.html)
    return render(request, 'admin_login.html')

@login_required
def upload_profile_picture(request):
    if request.method == "POST":
        profile = request.user.userprofile
        profile.profile_picture = request.FILES.get("profile_picture")
        profile.save()
    return redirect(request.META.get("HTTP_REFERER"))
