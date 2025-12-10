from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Dedicated route: /professor/profile
    path('professor/profile/', views.professor_profile_page, name='professor_profile_page'),
    # API route: /api/professors/{id}/profile
    path('api/professors/<int:pk>/profile', api_views.ProfessorProfileAPIView.as_view(), name='api_professor_profile'),
]