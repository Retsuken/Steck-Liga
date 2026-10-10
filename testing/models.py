from django.db import models
from catalog.choices import SPECIALIZATIONS, GRADES
from candidates.models import CandidateProfile
from employers.models import Company


class Question(models.Model):
    class QType(models.TextChoices):
        MCQ = "mcq", "Выбор"
        PARAM = "param", "Параметризованная"

    specialization = models.CharField(max_length=40, choices=SPECIALIZATIONS)
    grade = models.CharField(max_length=20, choices=GRADES)
    skill = models.CharField(max_length=80, blank=True)
    difficulty = models.PositiveSmallIntegerField(default=2)
    qtype = models.CharField(max_length=10, choices=QType.choices)
    stem = models.TextField()
    options = models.JSONField(default=list, blank=True)
    answer_key = models.CharField(max_length=40)
    param_spec = models.JSONField(default=dict, blank=True)
    answer_expr = models.CharField(max_length=200, blank=True)
    discrimination = models.FloatField(default=1.0)

    def __str__(self):
        return f"{self.specialization}/{self.grade}: {self.stem[:60]}"


class TestAttempt(models.Model):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="attempts")
    specialization = models.CharField(max_length=40)
    target_grade = models.CharField(max_length=20)
    seed = models.CharField(max_length=64)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)
    strong_pass = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]


class AttemptItem(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="items")
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    order = models.PositiveSmallIntegerField()
    rendered_stem = models.TextField()
    rendered_options = models.JSONField(default=list, blank=True)
    correct_key = models.CharField(max_length=80)
    given_key = models.CharField(max_length=80, blank=True)
    is_correct = models.BooleanField(default=False)
    points = models.FloatField(default=1)


class EmployerChallenge(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="challenges")
    title = models.CharField(max_length=200)
    prompt = models.TextField()
    specialization = models.CharField(max_length=40, choices=SPECIALIZATIONS)
    grade = models.CharField(max_length=20, choices=GRADES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Assignment(models.Model):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="assignments")
    challenge = models.ForeignKey(EmployerChallenge, on_delete=models.CASCADE, related_name="assignments")
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    solution = models.TextField(blank=True)
    approach = models.TextField(blank=True)
    freshness_delta = models.SmallIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("profile", "challenge")
