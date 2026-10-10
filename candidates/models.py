from django.conf import settings
from django.db import models
from django.utils import timezone
from catalog.choices import SPECIALIZATIONS, GRADES, INDUSTRIES, category_code, category_label


class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate")
    full_name = models.CharField("ФИО", max_length=200, blank=True)
    phone = models.CharField("телефон", max_length=40, blank=True)
    city = models.CharField("город", max_length=120, blank=True)
    about = models.TextField("о себе", blank=True)
    stack = models.JSONField("стек", default=list, blank=True)
    soft_skills = models.JSONField("софт-скиллы", default=list, blank=True)
    years_experience = models.DecimalField("стаж, лет", max_digits=4, decimal_places=1, default=0)
    industry = models.CharField("отрасль", max_length=40, choices=INDUSTRIES, blank=True)
    specialization = models.CharField("специализация", max_length=40, choices=SPECIALIZATIONS, blank=True)
    claimed_grade = models.CharField("заявленный грейд", max_length=20, choices=GRADES, blank=True)
    confirmed_grade = models.CharField("подтверждённый грейд", max_length=20, choices=GRADES, blank=True)
    last_test_score = models.PositiveSmallIntegerField(default=0)
    last_grade_change_at = models.DateTimeField(null=True, blank=True)
    last_assignment_at = models.DateTimeField(null=True, blank=True)
    freshness_score = models.PositiveSmallIntegerField(default=50)
    fsp_id = models.CharField("ID участника ФСП", max_length=64, blank=True)
    publish_profile = models.BooleanField("публиковать профиль работодателям", default=True)
    show_fsp = models.BooleanField("показывать достижения ФСП", default=True)
    show_about = models.BooleanField("показывать описание", default=True)
    show_stack = models.BooleanField("показывать стек", default=True)
    consent_publish = models.BooleanField("согласие на публикацию профиля", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "профиль кандидата"
        verbose_name_plural = "профили кандидатов"

    def __str__(self):
        return self.full_name or self.user.email

    @property
    def category(self):
        if self.specialization and self.confirmed_grade:
            return category_code(self.specialization, self.confirmed_grade)
        return ""

    @property
    def category_label(self):
        if self.specialization and self.confirmed_grade:
            return category_label(self.specialization, self.confirmed_grade)
        return "Категория не присвоена"

    @property
    def has_fsp(self):
        return bool(self.fsp_id) and self.achievements.exists()

    @property
    def fsp_points(self):
        if not self.show_fsp:
            return 0
        return sum(a.rating_points for a in self.achievements.all())

    def days_until_grade_change(self):
        if not self.last_grade_change_at:
            return 0
        delta = timezone.now() - self.last_grade_change_at
        left = settings.GRADE_CHANGE_DAYS - delta.days
        return max(0, left)

    def can_change_grade(self):
        return self.days_until_grade_change() == 0


class Experience(models.Model):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="experience")
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    years = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    description = models.TextField(blank=True)


class FspAchievement(models.Model):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="achievements")
    event_name = models.CharField("мероприятие", max_length=240)
    year = models.PositiveSmallIntegerField()
    place = models.PositiveSmallIntegerField("место", null=True, blank=True)
    rating_points = models.PositiveIntegerField("рейтинговые очки", default=0)
    discipline = models.CharField("дисциплина", max_length=120, blank=True)
    verified = models.BooleanField(default=True)

    class Meta:
        ordering = ["-year", "-rating_points"]


class GradeHistory(models.Model):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="grade_history")
    specialization = models.CharField(max_length=40)
    from_grade = models.CharField(max_length=20, blank=True)
    to_grade = models.CharField(max_length=20)
    score = models.PositiveSmallIntegerField(default=0)
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
