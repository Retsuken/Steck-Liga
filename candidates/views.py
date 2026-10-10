from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from catalog.choices import GRADES, INDUSTRIES, SPECIALIZATIONS, STACK_CATALOG
from candidates.models import CandidateProfile, Experience
from candidates.pdf_profile import build_profile_pdf
from candidates.resume import extract_pdf_text, parse_resume_text
from matching.models import Invitation
from testing.assignments import maybe_assign, submit_assignment
from testing.engine import attempt_expired, finish_attempt, start_attempt
from testing.grading import apply_test_result, confirm_grade
from testing.models import TestAttempt
from vacancies.models import Application, Vacancy


def _profile(request) -> CandidateProfile:
    return request.user.candidate


@role_required("candidate")
def dashboard(request):
    p = _profile(request)
    maybe_assign(p)
    return render(
        request,
        "candidate/dashboard.html",
        {
            "p": p,
            "invites": p.invitations.all()[:5],
            "assignments": p.assignments.filter(submitted_at__isnull=True)[:3],
            "attempts": p.attempts.all()[:5],
        },
    )


@role_required("candidate")
def profile_edit(request):
    p = _profile(request)
    if request.method == "POST":
        p.full_name = request.POST.get("full_name", "").strip()
        p.phone = request.POST.get("phone", "").strip()
        p.city = request.POST.get("city", "").strip()
        p.about = request.POST.get("about", "").strip()
        p.years_experience = request.POST.get("years_experience") or 0
        p.stack = [s.strip() for s in request.POST.get("stack", "").split(",") if s.strip()]
        p.soft_skills = [s.strip() for s in request.POST.get("soft_skills", "").split(",") if s.strip()]
        p.save()
        messages.success(request, "Профиль сохранён.")
        return redirect("candidate_profile")
    return render(request, "candidate/profile.html", {"p": p, "stack_catalog": STACK_CATALOG})


@role_required("candidate")
def resume_upload(request):
    p = _profile(request)
    parsed = None
    if request.method == "POST" and request.FILES.get("pdf"):
        try:
            text = extract_pdf_text(request.FILES["pdf"])
            parsed = parse_resume_text(text)
            if parsed.get("full_name"):
                p.full_name = parsed["full_name"]
            if parsed.get("phone"):
                p.phone = parsed["phone"]
            if parsed.get("stack"):
                p.stack = list(dict.fromkeys((p.stack or []) + parsed["stack"]))
            if parsed.get("years_experience"):
                p.years_experience = parsed["years_experience"]
            if parsed.get("about") and not p.about:
                p.about = parsed["about"][:800]
            p.save()
            messages.success(request, "PDF разобран, поля профиля обновлены. Проверьте и поправьте вручную.")
        except Exception as exc:
            messages.error(request, f"Не удалось прочитать PDF: {exc}")
    if request.method == "POST" and request.POST.get("company"):
        Experience.objects.create(
            profile=p,
            company=request.POST.get("company"),
            role=request.POST.get("role"),
            years=request.POST.get("years") or 1,
            description=request.POST.get("description", ""),
        )
        messages.success(request, "Место работы добавлено.")
        return redirect("candidate_resume")
    return render(request, "candidate/resume.html", {"p": p, "parsed": parsed})


@role_required("candidate")
def profile_pdf(request):
    pdf = build_profile_pdf(_profile(request))
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = 'attachment; filename="stekliga-profile.pdf"'
    return resp


@role_required("candidate")
def survey(request):
    p = _profile(request)
    if request.method == "POST":
        p.industry = request.POST.get("industry", "")
        p.specialization = request.POST.get("specialization", "")
        p.claimed_grade = request.POST.get("claimed_grade", "")
        p.save()
        messages.info(request, "Опрос сохранён. Дальше — тест на заявленный грейд.")
        return redirect("candidate_test_start")
    return render(
        request,
        "candidate/survey.html",
        {"p": p, "industries": INDUSTRIES, "specs": SPECIALIZATIONS, "grades": GRADES},
    )


@role_required("candidate")
def test_start(request):
    p = _profile(request)
    grade = request.GET.get("grade") or p.claimed_grade
    if not p.specialization or not grade:
        messages.warning(request, "Сначала пройдите опрос: отрасль, специализация, грейд.")
        return redirect("candidate_survey")
    if request.method == "POST":
        open_attempt = p.attempts.filter(finished_at__isnull=True).first()
        if open_attempt and not attempt_expired(open_attempt):
            return redirect("candidate_test_take", pk=open_attempt.pk)
        attempt = start_attempt(p, p.specialization, grade)
        return redirect("candidate_test_take", pk=attempt.pk)
    return render(request, "candidate/test_start.html", {"p": p, "grade": grade})


@role_required("candidate")
def test_take(request, pk):
    p = _profile(request)
    attempt = get_object_or_404(TestAttempt, pk=pk, profile=p, finished_at__isnull=True)
    if attempt_expired(attempt):
        finish_attempt(attempt, {})
        apply_test_result(p, attempt)
        messages.warning(request, "Время теста истекло, ответы отправлены как есть.")
        return redirect("candidate_test_result", pk=attempt.pk)
    if request.method == "POST":
        answers = {k.replace("q_", ""): v for k, v in request.POST.items() if k.startswith("q_")}
        finish_attempt(attempt, answers)
        info = apply_test_result(p, attempt)
        request.session["test_info"] = {k: v for k, v in info.items() if k != "assigned" or True}
        return redirect("candidate_test_result", pk=attempt.pk)
    return render(request, "candidate/test_take.html", {"p": p, "attempt": attempt, "items": attempt.items.all()})


@role_required("candidate")
def test_result(request, pk):
    p = _profile(request)
    attempt = get_object_or_404(TestAttempt, pk=pk, profile=p)
    info = apply_test_result(p, attempt) if attempt.finished_at else {}
    if request.method == "POST" and request.POST.get("confirm_grade"):
        ok = confirm_grade(p, request.POST["confirm_grade"], attempt.score, "Смена грейда по итогам теста")
        if ok:
            messages.success(request, "Категория обновлена.")
        else:
            messages.error(request, f"Смена грейда доступна через {p.days_until_grade_change()} дн.")
        return redirect("candidate_category")
    return render(request, "candidate/test_result.html", {"p": p, "attempt": attempt, "info": info})


@role_required("candidate")
def category(request):
    p = _profile(request)
    return render(request, "candidate/category.html", {"p": p})


@role_required("candidate")
def invitations(request):
    p = _profile(request)
    return render(request, "candidate/invitations.html", {"p": p, "items": p.invitations.all()})


@role_required("candidate")
def invitation_detail(request, pk):
    p = _profile(request)
    inv = get_object_or_404(Invitation, pk=pk, candidate=p)
    if inv.status == "sent":
        inv.status = "viewed"
        inv.viewed_at = timezone.now()
        inv.save(update_fields=["status", "viewed_at"])
    if request.method == "POST":
        action = request.POST.get("action")
        inv.candidate_reply = request.POST.get("reply", "")
        inv.resolved_at = timezone.now()
        inv.status = "accepted" if action == "accept" else "declined"
        inv.save()
        messages.success(request, "Решение сохранено. При принятии работодатель получит ваши контакты.")
        return redirect("candidate_invitations")
    return render(request, "candidate/invitation_detail.html", {"inv": inv})


@role_required("candidate")
def vacancy_list(request):
    p = _profile(request)
    qs = Vacancy.objects.filter(is_published=True).select_related("company")
    spec = request.GET.get("specialization")
    if spec:
        qs = qs.filter(specialization=spec)
    return render(request, "candidate/vacancies.html", {"p": p, "items": qs, "specs": SPECIALIZATIONS})


@role_required("candidate")
def vacancy_detail(request, pk):
    p = _profile(request)
    v = get_object_or_404(Vacancy, pk=pk, is_published=True)
    applied = p.applications.filter(vacancy=v).first()
    if request.method == "POST" and not applied:
        Application.objects.create(vacancy=v, candidate=p, cover_letter=request.POST.get("cover", ""))
        messages.success(request, "Отклик отправлен. Контакты станут видны работодателю.")
        return redirect("candidate_applications")
    return render(request, "candidate/vacancy_detail.html", {"v": v, "applied": applied})


@role_required("candidate")
def applications(request):
    p = _profile(request)
    return render(request, "candidate/applications.html", {"p": p, "items": p.applications.select_related("vacancy", "vacancy__company")})


@role_required("candidate")
def assignments_view(request):
    p = _profile(request)
    maybe_assign(p)
    return render(request, "candidate/assignments.html", {"p": p, "items": p.assignments.select_related("challenge", "challenge__company")})


@role_required("candidate")
def assignment_submit(request, pk):
    p = _profile(request)
    item = get_object_or_404(p.assignments, pk=pk, submitted_at__isnull=True)
    if request.method == "POST":
        submit_assignment(item, request.POST.get("solution", ""), request.POST.get("approach", ""))
        messages.success(request, "Решение отправлено, свежесть профиля повышена.")
        return redirect("candidate_assignments")
    return render(request, "candidate/assignment_form.html", {"item": item})


@role_required("candidate")
def settings_view(request):
    p = _profile(request)
    if request.method == "POST":
        p.publish_profile = request.POST.get("publish_profile") == "on"
        p.show_fsp = request.POST.get("show_fsp") == "on"
        p.show_about = request.POST.get("show_about") == "on"
        p.show_stack = request.POST.get("show_stack") == "on"
        p.consent_publish = request.POST.get("consent_publish") == "on"
        p.fsp_id = request.POST.get("fsp_id", "").strip()
        p.save()
        messages.success(request, "Настройки сохранены.")
        return redirect("candidate_settings")
    return render(request, "candidate/settings.html", {"p": p})
