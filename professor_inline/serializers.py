from rest_framework import serializers
from .models import Professor

class ProfessorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number', 
            'department', 'office_location', 'profile_picture'
        ]
        # FIX 2: Explicitly set non-editable fields as read-only for API security
        read_only_fields = ['id', 'first_name', 'last_name', 'email']