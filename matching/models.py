from django.db import models
from catalog.choices import INVITE_STATUSES
from candidates.models import CandidateProfile
from employers.models import Company, HiringNeed
from vacancies.models import Vacancy


class Invitation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invitations")
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="invitations")
    need = models.ForeignKey(HiringNeed, on_delete=models.SET_NULL, null=True, blank=True)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.SET_NULL, null=True, blank=True)
    offer_text = models.TextField("описание предложения")
    salary_from = models.PositiveIntegerField("зарплата от, ₽")
    salary_to = models.PositiveIntegerField("зарплата до, ₽")
    contact_method = models.CharField("способ связи работодателя", max_length=240)
    status = models.CharField(max_length=20, choices=INVITE_STATUSES, default="sent")
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    candidate_reply = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def salary_range(self):
        return f"{self.salary_from:,} – {self.salary_to:,} ₽".replace(",", " ")


class SavedShortlist(models.Model):
    """Сохраняет текущую подборку, чтобы фильтры её не затирали."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="shortlists")
    need = models.ForeignKey(HiringNeed, on_delete=models.CASCADE, related_name="shortlists", null=True, blank=True)
    title = models.CharField(max_length=200, default="Подборка")
    candidate_ids = models.JSONField(default=list)
    filters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
