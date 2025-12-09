from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Professor 

@login_required 
def professor_profile_page(request):
    # Create the Professor profile if it doesn't exist for the logged-in user
    professor, created = Professor.objects.get_or_create(user=request.user) 
    
    professor_pk = professor.pk
    
    # Use User model's data for first/last name and email if Professor doesn't shadow them
    # Assuming Professor model has a 'user' Foreign Key
    
    context = {
        'professor': professor,
        'professor_pk': professor_pk, 
        
        # Correctly retrieving data (assuming User fields are linked)
        'first_name': professor.first_name,
        'last_name': professor.last_name,
        
        
        'email': professor.email, # This field is READONLY in the design
        
        # Editable fields (make sure these exist in your Professor model!)
        'phone_number': getattr(professor, 'phone_number', ''), 
        'department': professor.department,
        'office_location': professor.office_location, 

        'api_url': f'/api/professors/{professor_pk}/profile',
    }
    return render(request, 'professor_inline/profile.html', context)