import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Нужен email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Кандидат"
        EMPLOYER = "employer", "Работодатель"

    username = None
    email = models.EmailField("email", unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    email_confirmed = models.BooleanField(default=False)
    consent_pd = models.BooleanField("согласие на обработку ПДн (152-ФЗ)", default=False)
    consent_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def is_candidate(self):
        return self.role == self.Role.CANDIDATE

    @property
    def is_employer(self):
        return self.role == self.Role.EMPLOYER


class EmailConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])
