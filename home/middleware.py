from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import secrets
import base64


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


class CSPMiddleware:
    """
    Middleware that sets a Content-Security-Policy header on responses.

    In DEBUG mode the policy is applied as Report-Only to avoid breaking development.
    The policy includes common sources required by the app (self, S3 media, Google OAuth,
    Google fonts and analytics). You can extend the lists using environment variables
    if necessary.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate a per-request nonce and attach it to the request so templates
        # can use it for inline scripts/styles: e.g. <script nonce="{{ request.csp_nonce }}">.
        raw = secrets.token_bytes(16)
        nonce = base64.b64encode(raw).decode('ascii').rstrip('=')
        request.csp_nonce = nonce

        response = self.get_response(request)

        # Build policy parts (tightened)
        s3_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)

        # No 'unsafe-inline' or 'unsafe-eval' — use nonces for inline scripts/styles instead
        script_src = ["'self'", f"'nonce-{nonce}'", 'https://accounts.google.com', 'https://apis.google.com', 'https://www.googletagmanager.com', 'https://www.google-analytics.com']
        style_src = ["'self'", f"'nonce-{nonce}'", 'https://fonts.googleapis.com']
        img_src = ["'self'", 'data:', 'blob:']
        connect_src = ["'self'", 'https://accounts.google.com', 'https://apis.google.com']
        font_src = ["'self'", 'https://fonts.gstatic.com', 'data:']

        if s3_domain:
            img_src.append(f'https://{s3_domain}')
            connect_src.append(f'https://{s3_domain}')

        # Join directives
        directives = [
            f"default-src 'self' https:",
            f"script-src {' '.join(script_src)}",
            f"style-src {' '.join(style_src)}",
            f"img-src {' '.join(img_src)}",
            f"connect-src {' '.join(connect_src)}",
            f"font-src {' '.join(font_src)}",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]

        policy = '; '.join(directives)

        # Use Report-Only in DEBUG to avoid breaking local development
        header_name = 'Content-Security-Policy-Report-Only' if settings.DEBUG else 'Content-Security-Policy'
        response[header_name] = policy

        # Also expose the nonce in a response header (optional) for easier debugging
        response['X-CSP-Nonce'] = nonce

        # Additional security headers
        # Referrer-Policy: prefer the one configured in settings, fallback to 'strict-origin-when-cross-origin'
        referrer_policy = getattr(settings, 'SECURE_REFERRER_POLICY', 'strict-origin-when-cross-origin')
        response.setdefault('Referrer-Policy', referrer_policy)

        # X-Content-Type-Options
        response.setdefault('X-Content-Type-Options', 'nosniff')

        # Permissions-Policy to disable powerful APIs by default
        # Adjust the list if your app needs specific features
        permissions_policy = (
            "geolocation=(), microphone=(), camera=(), payment=(), usb=(), geolocation=()"
        )
        response.setdefault('Permissions-Policy', permissions_policy)

        return response
