from flask import session,redirect
from functools import wraps


def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session or session.get('role') != role:
                return redirect(f'/{role}_login')
            return f(*args, **kwargs)
        return decorated_function
    return decorator