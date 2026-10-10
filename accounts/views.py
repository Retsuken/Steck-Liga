from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.models import EmailConfirmation, User
from candidates.models import CandidateProfile
from employers.models import Company


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "pages/home.html")


def register(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        role = request.POST.get("role")
        consent = request.POST.get("consent_pd") == "on"
        if not consent:
            messages.error(request, "Нужно согласие на обработку персональных данных (152-ФЗ).")
            return render(request, "auth/register.html")
        if password != password2 or len(password) < 8:
            messages.error(request, "Пароль не менее 8 символов, поля должны совпадать.")
            return render(request, "auth/register.html")
        if role not in (User.Role.CANDIDATE, User.Role.EMPLOYER):
            messages.error(request, "Выберите роль.")
            return render(request, "auth/register.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Этот email уже зарегистрирован.")
            return render(request, "auth/register.html")
        user = User.objects.create_user(
            email=email,
            password=password,
            role=role,
            consent_pd=True,
            consent_at=timezone.now(),
        )
        if role == User.Role.CANDIDATE:
            CandidateProfile.objects.create(user=user)
        else:
            Company.objects.create(user=user, name="", contact_email=email)
        token = EmailConfirmation.objects.create(user=user)
        confirm_url = request.build_absolute_uri(reverse("confirm_email", args=[token.token]))
        print(f"[email] Подтверждение адреса {email}: {confirm_url}")
        request.session["pending_email"] = email
        request.session["demo_confirm_url"] = confirm_url
        messages.success(request, "Аккаунт создан. Подтвердите email по ссылке.")
        return redirect("confirm_pending")
    return render(request, "auth/register.html")


def confirm_pending(request):
    return render(
        request,
        "auth/confirm_pending.html",
        {
            "confirm_url": request.session.get("demo_confirm_url"),
            "email": request.session.get("pending_email"),
        },
    )


def confirm_email(request, token):
    rec = get_object_or_404(EmailConfirmation, token=token, used_at__isnull=True)
    rec.user.email_confirmed = True
    rec.user.save(update_fields=["email_confirmed"])
    rec.mark_used()
    login(request, rec.user)
    messages.success(request, "Email подтверждён. Добро пожаловать в СтекЛигу.")
    return redirect("dashboard")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        if user and user.check_password(password):
            if not user.email_confirmed:
                request.session["pending_email"] = email
                messages.warning(request, "Сначала подтвердите email.")
                return redirect("confirm_pending")
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Неверный email или пароль.")
    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    if request.user.is_candidate:
        return redirect("candidate_dashboard")
    if request.user.is_employer:
        return redirect("employer_dashboard")
    return redirect("home")


def pitch(request):
    return render(request, "pages/pitch.html")
