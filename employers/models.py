from django.conf import settings
from django.db import models
from catalog.choices import SPECIALIZATIONS, GRADES, INDUSTRIES


class Company(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company")
    name = models.CharField("название", max_length=200)
    description = models.TextField("описание", blank=True)
    industry = models.CharField("направление", max_length=40, choices=INDUSTRIES, blank=True)
    city = models.CharField(max_length=120, blank=True)
    site = models.URLField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    contact_email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class HiringNeed(models.Model):
    """Описание потребности — основа подборки, не обязательно вакансия."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="needs")
    title = models.CharField("кого ищем", max_length=200)
    team_about = models.TextField("чем занимается команда", blank=True)
    description = models.TextField("описание потребности")
    specialization = models.CharField(max_length=40, choices=SPECIALIZATIONS)
    grade = models.CharField(max_length=20, choices=GRADES)
    stack = models.JSONField(default=list, blank=True)
    salary_from = models.PositiveIntegerField("зарплата от, ₽")
    salary_to = models.PositiveIntegerField("зарплата до, ₽")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company.name}: {self.title}"
