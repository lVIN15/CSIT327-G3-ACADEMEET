from django.urls import path
from .views import professor_profile_page
from .api_views import ProfessorProfileAPIView
from . import views
from . import api_views

urlpatterns = [
    # Dedicated route: /professor/profile
   path('profile/', views.professor_profile_page, name='professor-profile'),
    # API route: /api/professors/{id}/profile
    path('professor/profile/', views.professor_profile_page, name='professor_profile_page'),
path('api/professors/<int:pk>/profile', api_views.ProfessorProfileAPIView.as_view(), name='api_professor_profile'),
]