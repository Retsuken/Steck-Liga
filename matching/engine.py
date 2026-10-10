"""Механика подбора.

Категория кандидата = специализация + подтверждённый тестом грейд.
Самоописание резюме на выдачу не влияет.

Ранжирование внутри категории и относительно потребности:
  0.40 * нормализованный балл теста
  0.25 * достижения ФСП (0, если истории нет — корректный кейс)
  0.20 * пересечение стека с потребностью
  0.15 * свежесть (регулярные задания)

Работодатель видит краткое обоснование каждой позиции.
"""

from __future__ import annotations

from catalog.choices import GRADE_ORDER, category_label
from candidates.models import CandidateProfile


def stack_overlap(a: list, b: list) -> float:
    sa, sb = {x.lower() for x in a or []}, {x.lower() for x in b or []}
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def fsp_norm(points: int) -> float:
    return min(1.0, points / 400.0)


def match_candidates(need, extra_filters: dict | None = None):
    qs = (
        CandidateProfile.objects.select_related("user")
        .prefetch_related("achievements")
        .filter(
            user__email_confirmed=True,
            publish_profile=True,
            consent_publish=True,
            confirmed_grade__gt="",
            specialization__gt="",
        )
    )
    extra_filters = extra_filters or {}
    if extra_filters.get("specialization"):
        qs = qs.filter(specialization=extra_filters["specialization"])
    else:
        qs = qs.filter(specialization=need.specialization)
    if extra_filters.get("grade"):
        qs = qs.filter(confirmed_grade=extra_filters["grade"])
    if extra_filters.get("fsp_only"):
        qs = qs.exclude(fsp_id="").exclude(achievements=None)
    if extra_filters.get("stack"):
        wanted = extra_filters["stack"].lower()
        qs = [p for p in qs if any(wanted in s.lower() for s in (p.stack or []))]
    else:
        qs = list(qs)

    scored = []
    for profile in qs:
        reasons = []
        cat_bonus = 0.0
        if profile.specialization == need.specialization and profile.confirmed_grade == need.grade:
            cat_bonus = 1.0
            reasons.append(f"Точное попадание в категорию «{profile.category_label}»")
        elif profile.specialization == need.specialization:
            dist = abs(GRADE_ORDER.get(profile.confirmed_grade, 0) - GRADE_ORDER.get(need.grade, 0))
            cat_bonus = max(0.0, 1 - 0.35 * dist)
            reasons.append(f"Та же специализация, грейд {profile.get_confirmed_grade_display()}")
        else:
            cat_bonus = 0.15
            reasons.append("Смежная специализация")

        test_n = profile.last_test_score / 100
        reasons.append(f"Тест: {profile.last_test_score}%")

        fsp = fsp_norm(profile.fsp_points)
        if profile.has_fsp and profile.show_fsp:
            reasons.append(f"ФСП: {profile.fsp_points} очков, {profile.achievements.count()} событий")
        else:
            reasons.append("История ФСП отсутствует — оценка только по тесту и стеку")

        ov = stack_overlap(profile.stack, need.stack)
        if ov:
            common = set(x.lower() for x in profile.stack) & set(x.lower() for x in need.stack)
            reasons.append("Стек: " + ", ".join(sorted(common)))
        fresh = profile.freshness_score / 100

        total = 100 * (
            0.28 * cat_bonus
            + 0.32 * test_n
            + 0.20 * fsp
            + 0.12 * ov
            + 0.08 * fresh
        )
        scored.append(
            {
                "profile": profile,
                "score": round(total, 1),
                "reasons": reasons,
                "category": profile.category_label,
            }
        )
    scored.sort(key=lambda x: (-x["score"], -x["profile"].last_test_score, -x["profile"].fsp_points))
    return scored


def bank_candidates(filters: dict):
    qs = (
        CandidateProfile.objects.select_related("user")
        .prefetch_related("achievements")
        .filter(
            user__email_confirmed=True,
            publish_profile=True,
            consent_publish=True,
            confirmed_grade__gt="",
        )
    )
    if filters.get("specialization"):
        qs = qs.filter(specialization=filters["specialization"])
    if filters.get("grade"):
        qs = qs.filter(confirmed_grade=filters["grade"])
    if filters.get("fsp_only"):
        qs = qs.exclude(fsp_id="")
    qs = list(qs)
    if filters.get("stack"):
        wanted = filters["stack"].lower()
        qs = [p for p in qs if any(wanted in s.lower() for s in (p.stack or []))]

    ranked = []
    for p in qs:
        fsp = fsp_norm(p.fsp_points)
        total = 0.55 * (p.last_test_score / 100) + 0.30 * fsp + 0.15 * (p.freshness_score / 100)
        ranked.append(
            {
                "profile": p,
                "score": round(100 * total, 1),
                "reasons": [
                    f"Категория {p.category_label}",
                    f"Тест {p.last_test_score}%",
                    f"ФСП {p.fsp_points} очков" if p.has_fsp else "Без истории ФСП",
                ],
                "category": p.category_label,
            }
        )
    ranked.sort(key=lambda x: (-x["score"], -x["profile"].fsp_points))
    return ranked


def contacts_visible(viewer_company, profile: CandidateProfile) -> bool:
    from matching.models import Invitation
    from vacancies.models import Application

    if Invitation.objects.filter(company=viewer_company, candidate=profile, status="accepted").exists():
        return True
    if Application.objects.filter(vacancy__company=viewer_company, candidate=profile).exists():
        return True
    return False
