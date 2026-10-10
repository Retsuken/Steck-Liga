from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from testing.models import Assignment, EmployerChallenge


def maybe_assign(profile):
    if not profile.specialization:
        return None
    last = profile.last_assignment_at
    if last and timezone.now() < last + timedelta(days=settings.ASSIGNMENT_PERIOD_DAYS):
        return None
    existing_ids = profile.assignments.values_list("challenge_id", flat=True)
    challenge = (
        EmployerChallenge.objects.filter(specialization=profile.specialization)
        .exclude(id__in=existing_ids)
        .order_by("?")
        .first()
    )
    if not challenge:
        return None
    assignment = Assignment.objects.create(profile=profile, challenge=challenge)
    profile.last_assignment_at = timezone.now()
    profile.save(update_fields=["last_assignment_at"])
    return assignment


def submit_assignment(assignment, solution: str, approach: str):
    assignment.solution = solution
    assignment.approach = approach
    assignment.submitted_at = timezone.now()
    length = len((solution or "") + (approach or ""))
    assignment.freshness_delta = 12 if length > 80 else 6
    assignment.save()
    p = assignment.profile
    p.freshness_score = min(100, p.freshness_score + assignment.freshness_delta)
    p.save(update_fields=["freshness_score"])
