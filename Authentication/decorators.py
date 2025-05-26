from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from functools import wraps
from .utils import decode_jwt_token

def authentication_required():
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                raise AuthenticationFailed('Token is missing!')

            try:
                data = decode_jwt_token(token)
                request.user = {'id': data['user_id']}  # Ensure request.user is set as a dictionary

            except Exception as e:
                raise AuthenticationFailed(f'Token is invalid! {str(e)}')

            return view_func(request, *args, **kwargs)  # Pass request to the view function

        return _wrapped_view
    return decorator