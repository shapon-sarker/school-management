from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required(['admin'])(f)

def teacher_required(f):
    return role_required(['teacher', 'admin'])(f)

def student_required(f):
    return role_required(['student'])(f) 