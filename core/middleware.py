from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.http import JsonResponse

class RoleAwareMiddleware:
    """
    Middleware to ensure the authenticated user's role matches the X-Role header.
    APIs can use this to reject tokens from the wrong role.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Skip paths that don't need auth (login, register, etc.)
        self.whitelist = {
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/send-otp/',
            '/api/auth/verify-otp/',
            '/api/auth/config/',
            '/api/auth/health/',
            '/api/auth/root/',
        }

    def __call__(self, request):
        path = request.path
        # We only check roles for /api/ routes
        if not path.startswith('/api/'):
            return self.get_response(request)

        # Get X-Role header early
        x_role = request.headers.get('X-Role')

        # Fast whitelist check
        if any(w in path for w in self.whitelist):
             return self.get_response(request)

        # Force JWT authentication for the middleware check
        if not request.user.is_authenticated:
            try:
                auth = JWTAuthentication().authenticate(request)
                if auth:
                    request.user, _ = auth
            except Exception:
                pass

        # If user is authenticated, check their role
        if request.user.is_authenticated:
            user_role = getattr(request.user, 'role', None)
            
            # ADMIN can access everything
            if user_role == 'ADMIN':
                return self.get_response(request)
                
            if x_role and x_role.upper() != user_role:
                return JsonResponse({
                    'error': 'INVALID_ROLE_TOKEN',
                    'message': f'Provided token is for role {user_role}, but request is for {x_role}'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Double check against URL path as a safety measure
            if '/api/rider/' in path and user_role != 'RIDER':
                return JsonResponse({
                    'error': 'INVALID_ROLE_TOKEN',
                    'message': 'Rider API requires a Rider token'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
            if '/api/restaurant/' in path and user_role != 'RESTAURANT':
                return JsonResponse({
                    'error': 'INVALID_ROLE_TOKEN',
                    'message': 'Restaurant API requires a Restaurant token'
                }, status=status.HTTP_401_UNAUTHORIZED)

        return self.get_response(request)
