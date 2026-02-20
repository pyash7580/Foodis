from django.shortcuts import redirect
from functools import wraps

def rider_required(view_func):
    """
    Decorator for views that checks if a rider is authenticated via session.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'rider_phone' not in request.session:
            return redirect('rider:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
