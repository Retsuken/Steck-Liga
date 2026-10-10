from django.utils import timezone
from catalog.choices import GRADE_ORDER, GRADES
from candidates.models import GradeHistory


def adjacent(grade: str, direction: int) -> str | None:
    codes = [g[0] for g in GRADES]
    i = GRADE_ORDER[grade] + direction
    if 0 <= i < len(codes):
        return codes[i]
    return None


def apply_test_result(profile, attempt) -> dict:
    """Грейд не понижается принудительно. Смена — только по решению кандидата и с кулдауном."""
    info = {
        "assigned": False,
        "can_try_lower": False,
        "can_try_higher": False,
        "lower": None,
        "higher": None,
        "cooldown_days": profile.days_until_grade_change(),
    }
    if attempt.passed:
        if not profile.confirmed_grade:
            profile.confirmed_grade = attempt.target_grade
            profile.last_grade_change_at = timezone.now()
            info["assigned"] = True
            GradeHistory.objects.create(
                profile=profile,
                specialization=attempt.specialization,
                from_grade="",
                to_grade=attempt.target_grade,
                score=attempt.score,
                note="Первичное присвоение категории",
            )
        profile.last_test_score = attempt.score
        profile.save()
        if attempt.strong_pass:
            info["can_try_higher"] = profile.can_change_grade()
            info["higher"] = adjacent(attempt.target_grade, 1)
        if attempt.target_grade != profile.confirmed_grade and profile.can_change_grade():
            # успешно сдал другой грейд — можно зафиксировать
            info["can_confirm_target"] = True
    else:
        profile.last_test_score = attempt.score
        profile.save()
        info["can_try_lower"] = True
        info["lower"] = adjacent(attempt.target_grade, -1)
    return info


def confirm_grade(profile, new_grade: str, score: int, note: str):
    if not profile.can_change_grade() and profile.confirmed_grade:
        return False
    old = profile.confirmed_grade
    profile.confirmed_grade = new_grade
    profile.last_grade_change_at = timezone.now()
    profile.save()
    GradeHistory.objects.create(
        profile=profile,
        specialization=profile.specialization,
        from_grade=old,
        to_grade=new_grade,
        score=score,
        note=note,
    )
    return True
