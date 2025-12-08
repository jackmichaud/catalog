from django.shortcuts import redirect
from django.urls import reverse

class ProfileSetupMiddleware:
    """
    Middleware to ensure authenticated users complete their profile setup
    before accessing the rest of the application.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for unauthenticated users
        if request.user.is_authenticated:
            # Skip if profile is already completed
            if not request.user.profile_completed:
                # Skip redirect if already on profile page, logout, or static/media files
                allowed_paths = [
                    reverse('profile'),
                    reverse('account_logout'),
                    '/static/',
                    '/media/',
                    '/accounts/',  # Allow allauth URLs
                ]
                
                if not any(request.path.startswith(path) for path in allowed_paths):
                    return redirect('profile')
        
        return self.get_response(request)
