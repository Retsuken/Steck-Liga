def nav_counters(request):
    ctx = {"invite_count": 0, "assign_count": 0, "app_count": 0}
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return ctx
    if user.is_candidate and hasattr(user, "candidate"):
        ctx["invite_count"] = user.candidate.invitations.filter(status__in=["sent", "viewed"]).count()
        ctx["assign_count"] = user.candidate.assignments.filter(submitted_at__isnull=True).count()
    if user.is_employer and hasattr(user, "company"):
        ctx["c"] = user.company
        ctx["app_count"] = sum(v.applications.filter(status="sent").count() for v in user.company.vacancies.all())
    if user.is_candidate and hasattr(user, "candidate"):
        ctx["p"] = user.candidate
    return ctx
