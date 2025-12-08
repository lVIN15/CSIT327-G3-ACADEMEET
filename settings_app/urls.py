from django.urls import path
from . import views

urlpatterns = [
    path('general/', views.general_settings, name='general_settings'),
    path('admin/', views.admin_settings, name='admin_settings'),
    path('teacher/', views.teacher_settings, name='teacher_settings'),
    path('student/', views.student_settings, name='student_settings'),
    
    # --- Additional Functional URLs (e.g., for Admin to manage users) ---
    path('admin/create_user/', views.create_user, name='create_user'),
    path('admin/edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    
    
    #NEW - NOV.18   
    # User Management Utilities (Updated to use 'admin/' prefix)
    path('admin/create_user/', views.create_user, name='create_user'),
    path('admin/edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    
    
    #NEW- NOV.16
    path('profile/<int:user_id>/', views.view_user_profile, name='view_user_profile'),
    
    #new nov19
      path('settings/', views.settings_view, name='settings'),
      path('student_settings/', views.settings_view, name='student_settings'),
     
    #new dec 3  
    path('api/admin/get-schedule/', views.get_professor_schedule_admin, name='get_professor_schedule_admin'),
      
    
    path('api/admin/get-schedule/', views.get_professor_schedule_admin, name='get_professor_schedule_admin'),
    
    # NEW URL FOR DELETING
    path('api/admin/delete-schedule/', views.delete_schedule_api, name='delete_schedule_api'),
]
