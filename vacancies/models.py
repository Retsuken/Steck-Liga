from django.db import models
from catalog.choices import SPECIALIZATIONS, GRADES, APPLICATION_STATUSES
from candidates.models import CandidateProfile
from employers.models import Company


class Vacancy(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="vacancies")
    title = models.CharField(max_length=200)
    description = models.TextField()
    specialization = models.CharField(max_length=40, choices=SPECIALIZATIONS)
    grade = models.CharField(max_length=20, choices=GRADES)
    stack = models.JSONField(default=list, blank=True)
    salary_from = models.PositiveIntegerField()
    salary_to = models.PositiveIntegerField()
    city = models.CharField(max_length=120, blank=True)
    remote = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "vacancies"

    def salary_range(self):
        return f"{self.salary_from:,} – {self.salary_to:,} ₽".replace(",", " ")

    def __str__(self):
        return self.title


class Application(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="applications")
    cover_letter = models.TextField("сопроводительное", blank=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUSES, default="sent")
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("vacancy", "candidate")
