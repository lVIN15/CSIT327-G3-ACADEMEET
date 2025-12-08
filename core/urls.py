from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # API endpoints
    path('api/holidays/', api_views.get_holidays_api, name='get_holidays'),
    path('api/holidays/<int:year>/<int:month>/', api_views.get_holidays_api, name='get_monthly_holidays'),
    path('', views.home, name='role_selection'),
    path('student/signup/', views.student_signup, name='student_signup'),
    path('teacher/signup/', views.teacher_signup, name='teacher_signup'),
    path('student/login/', views.student_login, name='student_login'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('forgot-password/sent/', views.forgot_password_sent, name='forgot_password_sent'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password/success/', views.reset_password_success, name='reset_password_success'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('professor/dashboard/', views.professor_dashboard, name='professor_dashboard'),
    path('professor/<int:professor_id>/schedule/', views.professor_schedule_view, name='professor_schedule_view'),  # NEW
    path('professor/add-schedule/', views.add_schedule, name='add_schedule'),
    path('professor/edit-schedule/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
    path('professor/delete-schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('api/schedules/', views.get_schedules, name='get_schedules'),
     path('api/schedules/department/<str:dept_code>/', api_views.ScheduleDepartmentFilterView.as_view(), name='schedule-filter-by-department'), #NEW
    path('api/schedules/', api_views.ScheduleDayTimeFilterView.as_view(), name='schedule-filter-day-time'), #NEW
    path('logout/', views.logout_view, name='logout'),
    
    #NEW: FOR ADMIN
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    
    
 ]