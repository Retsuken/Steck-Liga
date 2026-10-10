"""Механика тестирования.

Устойчивость к распространению заданий:
1. Банк заданий стратифицирован по специализации, грейду и навыку.
2. Каждая попытка получает уникальную выборку (seed = user + attempt + время).
3. Параметризованные задачи меняют числа/ожидаемый ответ, поэтому «шпаргалка»
   с чужой попытки не совпадает.
4. Веса зависят от difficulty и discrimination — одинаковый набор «лёгких»
   вопросов не даёт высокий грейд.
"""

from __future__ import annotations

import random
from datetime import timedelta

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from catalog.choices import GRADE_ORDER, GRADES
from testing.models import AttemptItem, Question, TestAttempt


def neighboring_grades(grade: str) -> list[str]:
    order = GRADE_ORDER[grade]
    codes = [g[0] for g in GRADES]
    result = [grade]
    if order > 0:
        result.append(codes[order - 1])
    if order + 1 < len(codes):
        result.append(codes[order + 1])
    return result


def _eval_answer(expr: str, params: dict) -> str:
    safe = {"abs": abs, "min": min, "max": max, "round": round, "len": len, **params}
    return str(eval(expr, {"__builtins__": {}}, safe))  # noqa: S307  банк заданий контролируется


def render_question(question: Question, rng: random.Random) -> tuple[str, list, str]:
    if question.qtype == Question.QType.PARAM and question.param_spec:
        params = {}
        for name, spec in question.param_spec.items():
            params[name] = rng.randint(int(spec["min"]), int(spec["max"]))
        stem = question.stem.format(**params)
        key = _eval_answer(question.answer_expr, params)
        options = []
        if question.options:
            distractors = []
            for raw in question.options:
                distractors.append(str(_eval_answer(raw, params)))
            pool = list(dict.fromkeys([key] + distractors))
            rng.shuffle(pool)
            options = [{"key": str(i), "text": val} for i, val in enumerate(pool)]
            key = next(o["key"] for o in options if o["text"] == str(key))
        return stem, options, key

    options = list(question.options or [])
    rng.shuffle(options)
    return question.stem, options, question.answer_key


def start_attempt(profile, specialization: str, grade: str) -> TestAttempt:
    seed = f"{profile.id}:{specialization}:{grade}:{timezone.now().timestamp()}"
    rng = random.Random(seed)
    grades = neighboring_grades(grade)
    pool = list(
        Question.objects.filter(specialization=specialization).filter(
            Q(grade=grade) | Q(grade__in=grades)
        )
    )
    if len(pool) < settings.TEST_QUESTION_COUNT:
        pool = list(Question.objects.filter(Q(specialization=specialization) | Q(grade=grade)))
    rng.shuffle(pool)
    selected = pool[: settings.TEST_QUESTION_COUNT]
    attempt = TestAttempt.objects.create(
        profile=profile,
        specialization=specialization,
        target_grade=grade,
        seed=seed,
    )
    for i, q in enumerate(selected):
        stem, options, key = render_question(q, rng)
        weight = q.difficulty * q.discrimination
        AttemptItem.objects.create(
            attempt=attempt,
            question=q,
            order=i,
            rendered_stem=stem,
            rendered_options=options,
            correct_key=str(key),
            points=weight,
        )
    return attempt


def attempt_expired(attempt: TestAttempt) -> bool:
    return timezone.now() > attempt.started_at + timedelta(minutes=settings.TEST_MINUTES)


def finish_attempt(attempt: TestAttempt, answers: dict[str, str]) -> TestAttempt:
    total = 0.0
    gained = 0.0
    for item in attempt.items.all():
        given = str(answers.get(str(item.id), "")).strip()
        item.given_key = given
        item.is_correct = given == str(item.correct_key)
        item.save(update_fields=["given_key", "is_correct"])
        total += item.points
        if item.is_correct:
            gained += item.points
    score = int(round(100 * gained / total)) if total else 0
    attempt.score = score
    attempt.passed = score >= settings.TEST_PASS_SCORE
    attempt.strong_pass = score >= settings.TEST_STRONG_SCORE
    attempt.finished_at = timezone.now()
    attempt.save()
    return attempt
