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
                # Skip redirect if already on setup page, profile page, logout, or static/media files
                allowed_paths = [
                    reverse('first_time_setup'),
                    reverse('profile'),
                    reverse('account_logout'),
                    '/static/',
                    '/media/',
                    '/accounts/',  # Allow allauth URLs
                    '/api/notifications/',  # Allow notification API calls
                ]

                if not any(request.path.startswith(path) for path in allowed_paths):
                    return redirect('first_time_setup')

        return self.get_response(request)
