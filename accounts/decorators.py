from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def role_required(role):
    def decorator(view):
        @wraps(view)
        def inner(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if not request.user.email_confirmed and not request.user.is_superuser:
                messages.warning(request, "Подтвердите email, чтобы пользоваться кабинетом.")
                return redirect("confirm_pending")
            if request.user.role != role:
                messages.error(request, "Недостаточно прав для этого раздела.")
                return redirect("dashboard")
            return view(request, *args, **kwargs)

        return inner

    return decorator
