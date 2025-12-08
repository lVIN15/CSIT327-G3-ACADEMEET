from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser 
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Professor
from .serializers import ProfessorProfileSerializer

class ProfessorProfileAPIView(generics.RetrieveUpdateAPIView):
    queryset = Professor.objects.all()
    serializer_class = ProfessorProfileSerializer
    permission_classes = [IsAuthenticated]
    
    # 1. Ensure JSONParser is included
    parser_classes = (MultiPartParser, FormParser, JSONParser) 
    lookup_field = 'pk'
    
    def get_object(self):
        professor_pk = self.kwargs['pk']
        
        # 2. Logic: If Admin, get ANY profile. If Professor, get ONLY their own.
        if self.request.user.is_superuser:
            obj = get_object_or_404(self.get_queryset(), pk=professor_pk)
        else:
            obj = get_object_or_404(self.get_queryset(), pk=professor_pk, user=self.request.user)
            
        self.check_object_permissions(self.request, obj)
        return obj