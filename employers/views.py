from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from catalog.choices import GRADES, INDUSTRIES, SPECIALIZATIONS
from candidates.models import CandidateProfile
from employers.models import Company, HiringNeed
from matching.engine import bank_candidates, contacts_visible, match_candidates
from matching.models import Invitation, SavedShortlist
from testing.models import EmployerChallenge
from vacancies.models import Application, Vacancy


def _company(request) -> Company:
    return request.user.company


@role_required("employer")
def dashboard(request):
    c = _company(request)
    return render(
        request,
        "employer/dashboard.html",
        {
            "c": c,
            "needs": c.needs.all()[:5],
            "invites": c.invitations.all()[:5],
            "vacancies": c.vacancies.all()[:5],
        },
    )


@role_required("employer")
def company_edit(request):
    c = _company(request)
    if request.method == "POST":
        c.name = request.POST.get("name", "").strip()
        c.description = request.POST.get("description", "")
        c.industry = request.POST.get("industry", "")
        c.city = request.POST.get("city", "")
        c.site = request.POST.get("site", "")
        c.phone = request.POST.get("phone", "")
        c.contact_email = request.POST.get("contact_email", "")
        c.save()
        messages.success(request, "Профиль компании сохранён.")
        return redirect("employer_company")
    return render(request, "employer/company.html", {"c": c, "industries": INDUSTRIES})


@role_required("employer")
def need_list(request):
    return render(request, "employer/needs.html", {"items": _company(request).needs.all()})


@role_required("employer")
def need_edit(request, pk=None):
    c = _company(request)
    need = get_object_or_404(HiringNeed, pk=pk, company=c) if pk else None
    if request.method == "POST":
        data = dict(
            title=request.POST.get("title"),
            team_about=request.POST.get("team_about", ""),
            description=request.POST.get("description"),
            specialization=request.POST.get("specialization"),
            grade=request.POST.get("grade"),
            stack=[s.strip() for s in request.POST.get("stack", "").split(",") if s.strip()],
            salary_from=int(request.POST.get("salary_from") or 0),
            salary_to=int(request.POST.get("salary_to") or 0),
        )
        if data["salary_from"] <= 0 or data["salary_to"] <= 0:
            messages.error(request, "Укажите диапазон зарплаты «от–до» в рублях — это обязательное требование.")
            return render(request, "employer/need_form.html", {"need": need, "specs": SPECIALIZATIONS, "grades": GRADES})
        if need:
            for k, v in data.items():
                setattr(need, k, v)
            need.save()
        else:
            need = HiringNeed.objects.create(company=c, **data)
        return redirect("employer_matches", pk=need.pk)
    return render(request, "employer/need_form.html", {"need": need, "specs": SPECIALIZATIONS, "grades": GRADES})


@role_required("employer")
def matches(request, pk):
    c = _company(request)
    need = get_object_or_404(HiringNeed, pk=pk, company=c)
    filters = {
        "specialization": request.GET.get("specialization") or "",
        "grade": request.GET.get("grade") or "",
        "stack": request.GET.get("stack") or "",
        "fsp_only": request.GET.get("fsp_only") == "1",
    }
    ranked = match_candidates(need, {k: v for k, v in filters.items() if v})
    if request.method == "POST" and request.POST.get("save_shortlist"):
        SavedShortlist.objects.create(
            company=c,
            need=need,
            title=request.POST.get("title") or f"Подборка {need.title}",
            candidate_ids=[x["profile"].id for x in ranked],
            filters=filters,
        )
        messages.success(request, "Подборка сохранена. Дальнейшие фильтры её не затирают.")
        return redirect("employer_shortlists")
    return render(
        request,
        "employer/matches.html",
        {
            "need": need,
            "ranked": ranked,
            "filters": filters,
            "specs": SPECIALIZATIONS,
            "grades": GRADES,
        },
    )


@role_required("employer")
def shortlists(request):
    return render(request, "employer/shortlists.html", {"items": _company(request).shortlists.select_related("need")})


@role_required("employer")
def bank(request):
    filters = {
        "specialization": request.GET.get("specialization") or "",
        "grade": request.GET.get("grade") or "",
        "stack": request.GET.get("stack") or "",
        "fsp_only": request.GET.get("fsp_only") == "1",
    }
    ranked = bank_candidates(filters)
    return render(
        request,
        "employer/bank.html",
        {"ranked": ranked, "filters": filters, "specs": SPECIALIZATIONS, "grades": GRADES},
    )


@role_required("employer")
def candidate_card(request, pk):
    c = _company(request)
    profile = get_object_or_404(
        CandidateProfile.objects.prefetch_related("achievements", "experience"),
        pk=pk,
        publish_profile=True,
        consent_publish=True,
        confirmed_grade__gt="",
    )
    visible = contacts_visible(c, profile)
    return render(request, "employer/candidate_card.html", {"p": profile, "visible": visible, "company": c})


@role_required("employer")
def invite_create(request, pk):
    c = _company(request)
    profile = get_object_or_404(CandidateProfile, pk=pk, publish_profile=True)
    if request.method == "POST":
        s_from = int(request.POST.get("salary_from") or 0)
        s_to = int(request.POST.get("salary_to") or 0)
        if s_from <= 0 or s_to <= 0:
            messages.error(request, "Зарплата «от–до» в рублях обязательна.")
        else:
            Invitation.objects.create(
                company=c,
                candidate=profile,
                need_id=request.POST.get("need") or None,
                vacancy_id=request.POST.get("vacancy") or None,
                offer_text=request.POST.get("offer_text", ""),
                salary_from=s_from,
                salary_to=s_to,
                contact_method=request.POST.get("contact_method") or c.contact_email or c.phone,
            )
            messages.success(request, "Приглашение отправлено. Контакты кандидата откроются после принятия.")
            return redirect("employer_invitations")
    return render(
        request,
        "employer/invite_form.html",
        {"p": profile, "needs": c.needs.all(), "vacancies": c.vacancies.all()},
    )


@role_required("employer")
def invitations(request):
    return render(
        request,
        "employer/invitations.html",
        {"items": _company(request).invitations.select_related("candidate")},
    )


@role_required("employer")
def vacancy_list(request):
    return render(request, "employer/vacancies.html", {"items": _company(request).vacancies.all()})


@role_required("employer")
def vacancy_edit(request, pk=None):
    c = _company(request)
    v = get_object_or_404(Vacancy, pk=pk, company=c) if pk else None
    if request.method == "POST":
        data = dict(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            specialization=request.POST.get("specialization"),
            grade=request.POST.get("grade"),
            stack=[s.strip() for s in request.POST.get("stack", "").split(",") if s.strip()],
            salary_from=int(request.POST.get("salary_from") or 0),
            salary_to=int(request.POST.get("salary_to") or 0),
            city=request.POST.get("city", ""),
            remote=request.POST.get("remote") == "on",
            is_published=request.POST.get("is_published") == "on",
        )
        if data["salary_from"] <= 0 or data["salary_to"] <= 0:
            messages.error(request, "Зарплата «от–до» обязательна.")
        elif v:
            for k, val in data.items():
                setattr(v, k, val)
            v.save()
            return redirect("employer_vacancies")
        else:
            Vacancy.objects.create(company=c, **data)
            return redirect("employer_vacancies")
    return render(request, "employer/vacancy_form.html", {"v": v, "specs": SPECIALIZATIONS, "grades": GRADES})


@role_required("employer")
def vacancy_apps(request, pk):
    c = _company(request)
    v = get_object_or_404(Vacancy, pk=pk, company=c)
    apps = v.applications.select_related("candidate")
    for a in apps.filter(status="sent"):
        a.status = "viewed"
        a.viewed_at = timezone.now()
        a.save(update_fields=["status", "viewed_at"])
    if request.method == "POST":
        app = get_object_or_404(Application, pk=request.POST.get("app_id"), vacancy=v)
        app.status = "accepted" if request.POST.get("action") == "accept" else "rejected"
        app.resolved_at = timezone.now()
        app.save()
        return redirect("employer_vacancy_apps", pk=pk)
    return render(request, "employer/vacancy_apps.html", {"v": v, "apps": v.applications.select_related("candidate")})


@role_required("employer")
def challenge_create(request):
    c = _company(request)
    if request.method == "POST":
        EmployerChallenge.objects.create(
            company=c,
            title=request.POST.get("title"),
            prompt=request.POST.get("prompt"),
            specialization=request.POST.get("specialization"),
            grade=request.POST.get("grade", ""),
        )
        messages.success(request, "Короткое задание добавлено в пул регулярных задач кандидатов.")
        return redirect("employer_dashboard")
    return render(request, "employer/challenge_form.html", {"specs": SPECIALIZATIONS, "grades": GRADES})
